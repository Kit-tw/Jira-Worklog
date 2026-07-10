import os
import tempfile

# Enum.py evaluates STORAGE_PATH at import time using USERPROFILE (Windows env var).
# On Linux/WSL test runs, set a temporary fallback so collection doesn't fail.
if "USERPROFILE" not in os.environ:
    _tmp = tempfile.mkdtemp()
    os.environ["USERPROFILE"] = _tmp
