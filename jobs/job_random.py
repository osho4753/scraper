# имитируем «работу»: бросаем кубик и выводим результат
import random
from datetime import datetime

now = datetime.utcnow().isoformat() + "Z"
value = random.randint(1, 6)
print(f"[{now}] job_random rolled: {value}", flush=True)
