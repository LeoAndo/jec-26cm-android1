"""同じ作業コピーの配布コマンドを直列化する（授業環境のmacOS/Linux用）。"""
from contextlib import contextmanager
import fcntl


@contextmanager
def distribution_lock(directory):
    directory.mkdir(parents=True, exist_ok=True)
    # ロック中のファイルを削除・置換すると別inodeへ並行取得できるため残す。
    with (directory / '.workflow.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
