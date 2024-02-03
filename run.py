import os
import sys
import logging
import datetime
from typing import Callable

from lib.view import gui

class StreamLogger:
    """Helper class to redirect stdout and stderr to the same log file as
    all python logging messages.

    Args:
        logfunc (Callable): function of the logger to be used to emit the
            message. Recommended to use the root logger, e.g. logging.info.
        streamtype (str): display string denoting the stream the message comes
            from, e.g. STDERR. This will be visible in the logs.

    Returns:
        None.
    """
    def __init__(self, logfunc: Callable, streamtype: str) -> None:
        self.logfunc = logfunc
        self.streamtype = streamtype
        self._msg = ""

    def write(self, msg: str) -> None:
        """Takes the message coming from the stream and logs it without
        newlines for better formatting.

        Args:
            msg (str): stream message; this should never need to be called
                explicitly since it overrides sys.<stream>.write.

        Returns:
            None.
        """
        self._msg = self._msg + msg
        while "\n" in self._msg:
            pos = self._msg.find("\n")
            self.logfunc(f"({self.streamtype}) {self._msg[:pos]}")
            self._msg = self._msg[pos+1:]

    def flush(self) -> None:
        """Dummy flush method put here in case some extra flushing logic
        is ever needed.

        Args:
            None.

        Returns:
            None.
        """
        pass

if __name__ == "__main__":
    logfn = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logfp = os.path.join("logs", logfn)

    logging.basicConfig(
        level=logging.DEBUG,
        filename=logfp,
        filemode="w",
        format="[%(levelname)s|%(filename)s|L%(lineno)s] %(asctime)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )

    sys.stdout = StreamLogger(logging.info, "STDOUT")
    sys.stderr = StreamLogger(logging.error, "STDERR")

    root = gui.App()
    root.mainloop()
