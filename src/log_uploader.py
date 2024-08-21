"""

"""

import os
import sys
import time
import timeout_decorator
from loguru import logger as log
import psutil
from glob import glob
from pathlib import Path
import zipfile
import random


LOOP_PERIOD = 5 # seconds
FREE_FILESYSTEM_SIZE_THRESH = 0.9
TOTAL_FILESYSTEM_SIZE = float(psutil.disk_usage('/').total)  # 10*1024**3 # 10GB
MAX_FILESYSTEM_SIZE = int(round(TOTAL_FILESYSTEM_SIZE * FREE_FILESYSTEM_SIZE_THRESH))
TMP_DIR = Path("test/fixtures")



def get_log_index(filename: str) -> int:
    period_idx = filename.find(".")
    return int(filename[4:period_idx])



def cleanup_space() -> bool:
    """ Function docs
    """

    file_list: list[str] = glob("file*.zip", root_dir = TMP_DIR) # returns a list of strings, which are (absolute) filenames of the log files in TMP_DIR
    file_list_sorted: list[str] = sorted(file_list, key = get_log_index) # sort the list of strings by the log index
    cur_idx = 0
    while True:
        disk_space_used: int = (random.randrange(1, 11) * 0.1) * TOTAL_FILESYSTEM_SIZE #psutil.disk_usage('/').used # returns bytes
        if disk_space_used > MAX_FILESYSTEM_SIZE:
            log.warning(f"Disk overage ({disk_space_used / TOTAL_FILESYSTEM_SIZE * 100:0.1f}%), deleting {file_list_sorted[cur_idx]}")
            #os.unlink(TMP_DIR / file_list_sorted[cur_idx]) # remove the file
            cur_idx += 1
            if cur_idx >= len(file_list):
                return False # indicate that we may not continue, deleted everything
        else:
            return True



def check_zip_file_valid(filename: Path) -> bool:
    try:
        zip_file = zipfile.ZipFile(filename)
        status = zip_file.testzip()
        if status is not None:
            log.trace(f"Archive {filename.name} failed the test")
            return False
    except Exception as exception_obj:
        if type(exception_obj) == zipfile.BadZipFile:
            log.trace(f"Archive {filename.name} is corrupt")
            return False
    return True



def cloud_upload(filename: Path) -> bool:
    """ A mock uploading function that just sleeps a random amount
    """

    time.sleep(random.randrange(int(round(LOOP_PERIOD * 1.1)))) # timeout 10% of the time
    if random.randrange(10) == 0:
        return False # make it fail 10%
    return True



@timeout_decorator.timeout(LOOP_PERIOD)
def cleanup_logs_dir() -> None:
    """ docs
    """

    if not cleanup_space():
        log.warning(f"Out of space after removing all logs")
        return

    file_list: list[str] = glob("file*.zip", root_dir = TMP_DIR)
    for cur_filename in file_list: # uploading in arbitrary order (but could use sorted order by reusing the logic in cleanup_space())
        if check_zip_file_valid(TMP_DIR / cur_filename):
            log.trace(f"Uploading {cur_filename}...")
            status: bool = cloud_upload(TMP_DIR / cur_filename)  # OS call wrapped in a timeout functionality that return False if timeout hit
            if status:
                log.trace(f"Done uploading {cur_filename}")
                #os.unlink(TMP_DIR / cur_filename) # remove the file
            else:
                log.error(f"Error uploading {cur_filename}, skipping...")
                



if __name__ == "__main__":
    # add argument support

    # TODO: setup the logger: file, CloudWatch, etc
    if not TMP_DIR.exists():
        log.error(f"Unable to open a logfile directory {TMP_DIR}")
        sys.exit(-1)

    while True:
        t_i: float = time.time()
        log.trace("Started upload check")
        try:
            cleanup_logs_dir()
        except Exception as exception_obj:
            if type(exception_obj) == timeout_decorator.timeout_decorator.TimeoutError:
                log.error("Timed out!")
            else:
                raise exception_obj
        t_f: float = time.time()
        t_remaining: float = LOOP_PERIOD - (t_f - t_i)
        if t_remaining > 0:
            log.trace(f"Done upload check, sleeping for {t_remaining:.1f}")
            time.sleep(t_remaining)
