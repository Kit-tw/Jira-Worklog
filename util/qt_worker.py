import asyncio
from PySide6.QtCore import QThread, Signal


class AsyncWorker(QThread):
    success = Signal(object)
    error = Signal(Exception)

    def __init__(self, coroutine, parent=None):
        super().__init__(parent)
        self._coroutine = coroutine

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._coroutine)
            self.success.emit(result)
        except Exception as e:
            self.error.emit(e)
        finally:
            loop.close()
