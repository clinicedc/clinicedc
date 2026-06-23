"""Download all PDF attachments from one or more Gmail accounts via IMAP.

Reads account credentials from a JSON file. Set the path via the
GMAIL_ACCOUNTS_FILE env var or the --accounts-file argument.

Accounts file format (e.g: .gmail_accounts.json):
    [
        {"email": "account1@gmail.com", "password": "xxxx xxxx xxxx xxxx"},
        {"email": "account2@gmail.com", "password": "yyyy yyyy yyyy yyyy"}
    ]

Usage:
    export GMAIL_ACCOUNTS_FILE=/path/to/accounts.json

    uv run --dev python -m edc_lab_results.scripts.download_gmail_pdfs \
        --email account1@gmail.com \
        --output-dir /path/to/pdf_downloads
        --accounts-file ~/.clinicedc/my_edc/.gmail_accounts.json

Features:
    - Tracks downloads in a manifest file (safe to re-run / resume).
    - Reconnects automatically on transient network errors (up to 3 retries).

After running this see the management command `import_labs`
"""

import argparse
import email
import imaplib
import json
import os
import socket
import sys
import time
from email.header import decode_header
from pathlib import Path

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 10
MANIFEST_FILENAME = ".downloaded_pdfs.json"


def decode_header_value(value: str) -> str:
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "._- " else "_" for c in name).strip()


def load_accounts(accounts_file: Path) -> list[dict[str, str]]:
    data = json.loads(accounts_file.read_text())
    if not isinstance(data, list) or not data:
        raise ValueError("Accounts file must be a non-empty JSON array.")
    for i, entry in enumerate(data):
        if "email" not in entry or "password" not in entry:
            raise ValueError(f"Account entry {i} missing 'email' or 'password'.")
    return data


def load_manifest(output_dir: Path) -> dict:
    """Load the manifest of previously downloaded attachments.

    Structure:
        {
            "<message_id>|<original_filename>": {
                "saved_as": "actual_file.pdf",
                "subject": "...",
                "date": "..."
            },
            ...
        }
    """
    manifest_path = output_dir / MANIFEST_FILENAME
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {}


def save_manifest(output_dir: Path, manifest: dict) -> None:
    manifest_path = output_dir / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2))


def make_manifest_key(message_id: str, original_filename: str) -> str:
    return f"{message_id}|{original_filename}"


def connect(
    email_address: str,
    password: str,
    imap_host: str,
) -> imaplib.IMAP4_SSL:
    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(email_address, password)
    mail.select('"[Gmail]/All Mail"')
    return mail


def download_pdf_attachments(
    email_address: str,
    password: str,
    output_dir: Path,
    *,
    imap_host: str = "imap.gmail.com",
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(output_dir)
    if manifest:
        print(f"Manifest has {len(manifest)} previously downloaded PDF(s) — will skip them.")

    print(f"Connecting to {imap_host} as {email_address} ...")
    mail = connect(email_address, password, imap_host)

    print("Searching for messages ...")
    status, data = mail.search(None, "ALL")
    if status != "OK":
        print("Search failed.")
        mail.logout()
        return 0

    message_ids = data[0].split()
    print(f"Found {len(message_ids)} messages. Scanning for PDF attachments ...")

    saved = 0
    skipped = 0
    i = 0
    while i < len(message_ids):
        msg_id = message_ids[i]
        i += 1

        try:
            status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError, socket.error) as e:
            mail = _reconnect_with_retry(e, email_address, password, imap_host, msg_index=i)
            status, data = mail.search(None, "ALL")
            if status != "OK":
                print("Search failed after reconnect.")
                break
            message_ids = data[0].split()
            i -= 1
            continue

        if status != "OK":
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        message_id = msg.get("Message-ID", f"unknown-{msg_id.decode()}")

        for part in msg.walk():
            content_type = part.get_content_type()
            filename = part.get_filename()
            if filename:
                filename = decode_header_value(filename)

            is_pdf = content_type == "application/pdf" or (
                filename and filename.lower().endswith(".pdf")
            )
            if not is_pdf or part.get("Content-Disposition") is None:
                continue

            original_filename = filename or f"attachment.pdf"
            filename = sanitize_filename(original_filename)
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"

            key = make_manifest_key(message_id, original_filename)
            if key in manifest:
                skipped += 1
                continue

            dest = output_dir / filename
            if dest.exists():
                stem = dest.stem
                suffix = dest.suffix
                n = 1
                while dest.exists():
                    dest = output_dir / f"{stem}_{n}{suffix}"
                    n += 1

            dest.write_bytes(part.get_payload(decode=True))

            subject = decode_header_value(msg.get("Subject", "(no subject)"))
            date = msg.get("Date", "(no date)")

            manifest[key] = {
                "saved_as": dest.name,
                "subject": subject,
                "date": date,
            }
            save_manifest(output_dir, manifest)

            print(f'  [{saved + 1}] {dest.name}  (subject: "{subject}", date: {date})')
            saved += 1

        if i % 100 == 0:
            print(f"  ... scanned {i}/{len(message_ids)} messages")

    try:
        mail.logout()
    except (imaplib.IMAP4.error, OSError):
        pass

    print(f"Done with {email_address}. {saved} PDF(s) saved, {skipped} skipped.\n")
    return saved


def _reconnect_with_retry(
    original_error: Exception,
    email_address: str,
    password: str,
    imap_host: str,
    *,
    msg_index: int,
) -> imaplib.IMAP4_SSL:
    for attempt in range(1, MAX_RETRIES + 1):
        print(
            f"\n  Connection lost at message {msg_index} ({original_error}). "
            f"Retrying in {RETRY_DELAY_SECONDS}s (attempt {attempt}/{MAX_RETRIES}) ..."
        )
        time.sleep(RETRY_DELAY_SECONDS)
        try:
            mail = connect(email_address, password, imap_host)
            print("  Reconnected.\n")
            return mail
        except (imaplib.IMAP4.error, OSError, socket.error) as e:
            original_error = e

    print(f"Failed to reconnect after {MAX_RETRIES} attempts.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download PDF attachments from one or more Gmail accounts."
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Gmail address to process (must exist in the accounts file)",
    )
    parser.add_argument(
        "--accounts-file",
        type=Path,
        default=None,
        help="Path to JSON accounts file (or set GMAIL_ACCOUNTS_FILE env var)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Local directory to save PDFs",
    )
    parser.add_argument(
        "--imap-host",
        default="imap.gmail.com",
        help="IMAP server (default: imap.gmail.com)",
    )
    args = parser.parse_args()

    accounts_file = args.accounts_file or os.environ.get("GMAIL_ACCOUNTS_FILE")
    if not accounts_file:
        print(
            "Error: provide --accounts-file or set GMAIL_ACCOUNTS_FILE env var.",
            file=sys.stderr,
        )
        sys.exit(1)
    accounts_file = Path(accounts_file)

    accounts = load_accounts(accounts_file)
    account = next((a for a in accounts if a["email"] == args.email), None)
    if not account:
        print(
            f"Error: '{args.email}' not found in {accounts_file}.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        saved = download_pdf_attachments(
            account["email"],
            account["password"],
            args.output_dir,
            imap_host=args.imap_host,
        )
    except imaplib.IMAP4.error as e:
        print(f"IMAP error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"All done. {saved} PDF(s) saved to {args.output_dir}")


if __name__ == "__main__":
    main()
