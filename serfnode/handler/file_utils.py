import os
from tempfile import mkstemp
import time


class atomic_write(object):
    """Perform an atomic write to a file.

    Use as::

        with atomic_write('/my_file') as f:
            f.write('foo')

    """

    def __init__(self, filepath):
        """
        :type filepath: str
        """
        self.filepath = filepath

    def __enter__(self):
        """
        :rtype: File
        """
        _, self.temp = mkstemp(dir=os.getcwd())
        self.f = open(self.temp, 'w')
        return self.f

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()
        if exc_type is None:
            os.rename(self.temp, self.filepath)


def wait_for_files(*filepath, **kwargs):
    """Wait for the existence of files.

    Warning: use ``atomic_write`` to write the file, since this function
    doesn't check that the file is complete.

    :type filepath: [str]
    :type kwargs: dict[str, float]
    :rtype: None
    """
    sleep_interval = kwargs.get('sleep_interval', 0.1)
    while not all(os.path.exists(f) for f in filepath):
        time.sleep(sleep_interval)
