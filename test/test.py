from pathlib import Path
import log_uploader


def test_get_log_index():
    assert log_uploader.get_log_index("file1.zip") == 1
    assert log_uploader.get_log_index("file23.zip") == 23
    assert log_uploader.get_log_index("file1024.zip") == 1024


def test_check_zip_file_valid():
    TMP_DIR = Path("test/fixtures")
    if not TMP_DIR.exists():
        raise IOError(f"Unable to read logfile dir {TMP_DIR}") 
    assert log_uploader.check_zip_file_valid(TMP_DIR / "file1.zip") == True
    assert log_uploader.check_zip_file_valid(TMP_DIR / "file2.zip") == False
    assert log_uploader.check_zip_file_valid(TMP_DIR / "file11.zip") == True