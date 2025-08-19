# печатаем дату/время, hostname и переменную окружения
import os, socket
from datetime import datetime

now = datetime.utcnow().isoformat() + "Z"
host = socket.gethostname()
msg = os.getenv("TEST_MESSAGE", "<unset>")

print(f"[{now}] HELLO from job_hello on {host}. TEST_MESSAGE={msg}", flush=True)
