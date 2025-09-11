import socket


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def scan_network(ip_range):
    open_printers = []
    for ip in ip_range:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # Timeout in seconds
            result = sock.connect_ex((ip, 9100))  # Port 9100 is common for network printers
            if result == 0:
                open_printers.append(ip)
            sock.close()
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    return open_printers


def get_ip_range(local_ip):
    ip_parts = local_ip.split(".")
    base_ip = ".".join(ip_parts[:3]) + "."
    return [base_ip + str(i) for i in range(1, 255)]


def main():
    local_ip = get_local_ip()
    ip_range = get_ip_range(local_ip)
    printers = scan_network(ip_range)
    if printers:
        print("Found network printers at the following IP addresses:")
        for printer in printers:
            print(printer)
    else:
        print("No network printers found.")


if __name__ == "__main__":
    main()
