import time
import cv2
import string
import threading
from collections import namedtuple
from typing import Optional

from eventkit import Event

Frame = namedtuple('Frame', ['time', 'image'])


class VideoStream(Event):
    """Expose a video stream as an :class:`~eventkit.Event`."""

    #: Default frame rate used when OpenCV cannot determine one.
    _DEFAULT_FPS = 30.0

    def __init__(self, camId=0, width=640, height=480, *, autostart: bool = True):
        super().__init__()
        self._args = camId, width, height
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        if autostart:
            self.start()

    def start(self) -> None:
        """Start the internal capture thread if it is not already running."""

        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        camId, width, height = self._args
        if isinstance(camId, int) or (isinstance(camId, str) and camId in string.digits):
            camId = int(camId)
            isLive = True
        else:
            isLive = isinstance(camId, str) and camId.startswith('http://')

        capture = cv2.VideoCapture(camId)
        if capture and capture.isOpened():
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            fps = capture.get(cv2.CAP_PROP_FPS) or self._DEFAULT_FPS
            if not fps or fps <= 0:
                fps = self._DEFAULT_FPS

            while not self._stop_event.is_set():
                if not capture.grab():
                    break
                t = time.perf_counter()
                retval, im = capture.retrieve()
                if not retval:
                    break
                frame = Frame(t, im)
                self.emit_threadsafe(frame)
                if not isLive and fps:
                    pause = t - time.perf_counter() + 1 / fps
                    if pause > 0 and self._stop_event.wait(pause):
                        break
            capture.release()
        self.done_event.emit_threadsafe(self)

    def stop(self, timeout: float = 1.0) -> bool:
        """Signal the capture thread to stop and wait for it to finish.

        Parameters
        ----------
        timeout:
            Maximum number of seconds to wait for the capture thread to exit.

        Returns
        -------
        bool
            ``True`` if the thread finished, ``False`` otherwise.
        """

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout)
        alive = self._thread is not None and self._thread.is_alive()
        self._thread = None if not alive else self._thread
        return not alive
