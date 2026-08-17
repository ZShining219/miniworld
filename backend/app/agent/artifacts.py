import tempfile
from pathlib import Path

TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".json", ".csv", ".log"}


def convert_uploaded_bytes(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in TEXT_SUFFIXES:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("utf-8", errors="replace")

    try:
        from markitdown import MarkItDown
    except ImportError as error:
        raise RuntimeError(
            "This file type requires the optional MarkItDown dependency"
        ) from error

    with tempfile.TemporaryDirectory(prefix="miniworld-import-") as temp_dir:
        path = Path(temp_dir) / f"artifact{suffix}"
        path.write_bytes(content)
        result = MarkItDown(enable_plugins=False).convert(str(path))
        text = result.text_content.strip()
        if not text:
            raise RuntimeError("The imported file did not contain readable text")
        return text
