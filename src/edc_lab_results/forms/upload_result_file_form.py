from django import forms

MAX_PDF_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB
PDF_MAGIC_BYTES = b"%PDF"


class _MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class _MultipleFileField(forms.FileField):
    """FileField that accepts multiple files."""

    def clean(self, data: object, initial: object = None) -> list:
        if not data or (isinstance(data, list) and not any(data)):
            if self.required:
                raise forms.ValidationError(self.error_messages["required"])
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [super(_MultipleFileField, self).clean(d, initial) for d in data]


class UploadResultFileForm(forms.Form):
    files = _MultipleFileField(
        widget=_MultipleFileInput(attrs={"accept": ".pdf"}),
        help_text="Select one or more PDF lab result files (max 1 MB each).",
    )

    def clean_files(self) -> list:
        """Run per-file PDF validation on all uploaded files."""
        files = self.cleaned_data.get("files", [])
        if files:
            self.validate_uploaded_files(files)
        return files

    @staticmethod
    def validate_uploaded_files(files: list) -> list:
        """Validate a list of uploaded files.

        Checks each file for:
        - ``.pdf`` extension
        - ``application/pdf`` content type
        - ``%PDF`` magic bytes header
        - Maximum file size
        """
        errors: list[str] = []
        for f in files:
            if not f.name.lower().endswith(".pdf"):
                errors.append(f"{f.name}: not a PDF file.")
                continue
            if f.content_type != "application/pdf":
                errors.append(f"{f.name}: unexpected content type ({f.content_type}).")
                continue
            if f.size > MAX_PDF_SIZE_BYTES:
                size_kb = f.size / 1024
                errors.append(f"{f.name}: file too large ({size_kb:.0f} KB, max 1 MB).")
                continue
            header = f.read(5)
            f.seek(0)
            if not header.startswith(PDF_MAGIC_BYTES):
                errors.append(f"{f.name}: file does not appear to be a valid PDF.")
                continue
        if errors:
            raise forms.ValidationError(errors)
        return files
