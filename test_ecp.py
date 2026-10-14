import pytest
from leaf_app.core import validate_upload
from helpers import make_leaf, make_image, pad_to

# Field 1: file extension  (valid: jpg/jpeg/png | invalid: other types | invalid: no extension)
ECP_EXT = [
    ("ECP01", "Valid class: JPG", "leaf.jpg", "JPEG", True),
    ("ECP02", "Valid class: PNG", "leaf.png", "PNG", True),
    ("ECP03", "Invalid class: GIF", "leaf.gif", "GIF", False),
    ("ECP04", "Invalid class: TXT", "leaf.txt", "PNG", False),
    ("ECP05", "Invalid class: no extension", "leaf", "PNG", False),
]

@pytest.mark.parametrize("tid,cls,name,fmt,expected", ECP_EXT, ids=[x[0] for x in ECP_EXT])
def test_ecp_file_extension(log, tid, cls, name, fmt, expected):
    data = make_image((100, 100), fmt)
    ok, msg = validate_upload(name, data)
    log(tid, "validate_upload (file type)", "ECP", f"{name} - {cls}", "Accept" if expected else "Reject", f"{'Accept' if ok else 'Reject'} ({msg})")
    assert ok == expected

# Field 2: image side length in pixels (invalid: <32 | valid: 32-4000)
ECP_SIZE = [
    ("ECP06", "Invalid class: < 32 px", (10, 10), False),
    ("ECP07", "Valid class: 32 - 4000 px", (256, 256), True),
]

@pytest.mark.parametrize("tid,cls,size,expected", ECP_SIZE, ids=[x[0] for x in ECP_SIZE])
def test_ecp_image_dimension(log, tid, cls, size, expected):
    ok, msg = validate_upload("leaf.png", make_image(size))
    log(tid, "validate_upload (dimensions)", "ECP", f"{size[0]}x{size[1]} px - {cls}", "Accept" if expected else "Reject", f"{'Accept' if ok else 'Reject'} ({msg})")
    assert ok == expected

# Field 3: file size in bytes (valid: 1 B - 5 MB | invalid: 0 B | invalid: > 5 MB)
ECP_BYTES = [
    ("ECP08", "Invalid class: 0 bytes", 0, False),
    ("ECP09", "Valid class: 1 B - 5 MB (2 MB)", 2 * 1024 * 1024, True),
    ("ECP10", "Invalid class: > 5 MB (8 MB)", 8 * 1024 * 1024, False),
]

@pytest.mark.parametrize("tid,cls,nbytes,expected", ECP_BYTES, ids=[x[0] for x in ECP_BYTES])
def test_ecp_file_size(log, tid, cls, nbytes, expected):
    data = b"" if nbytes == 0 else pad_to(make_image((100, 100)), nbytes)
    ok, msg = validate_upload("leaf.png", data)
    log(tid, "validate_upload (file size)", "ECP", f"{nbytes} bytes - {cls}", "Accept" if expected else "Reject", f"{'Accept' if ok else 'Reject'} ({msg})")
    assert ok == expected
