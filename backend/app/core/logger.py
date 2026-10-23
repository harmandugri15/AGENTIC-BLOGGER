import logging
import sys

class FlushStreamHandler(logging.StreamHandler):
    """Stream handler that immediately flushes every log record to the terminal."""
    def emit(self, record):
        try:
            super().emit(record)
            self.flush()
        except Exception:
            pass

_SHARED_HANDLER = None

def _get_shared_handler() -> logging.Handler:
    global _SHARED_HANDLER
    if _SHARED_HANDLER is None:
        _SHARED_HANDLER = FlushStreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        _SHARED_HANDLER.setFormatter(formatter)
    return _SHARED_HANDLER

def get_logger(name: str) -> logging.Logger:
    """Returns a logger guaranteed to write immediately to terminal stdout without buffering."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    shared_h = _get_shared_handler()
    if shared_h not in logger.handlers:
        logger.handlers = [shared_h]
        
    return logger

def setup_global_logging():
    """Configures root and uvicorn loggers to ensure all agent events appear in the terminal."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    shared_h = _get_shared_handler()
    if shared_h not in root.handlers:
        root.addHandler(shared_h)
