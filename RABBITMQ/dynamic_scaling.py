import multiprocessing
import pika
import time
import math
import csv
from datetime import datetime

from insult_service import insult_service

# Configuración
T = 0.004
C = 1 / T
CHECK_INTERVAL = 4

current_workers = []
last_queue_length = 0
CSV_FILE = "scaling_log.csv"

# Inicializa CSV si no existe
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["queue_length", "lambda", "required_workers", "active_workers"])

def get_queue_length():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    q = channel.queue_declare(queue='insult_queue', passive=True)
    queue_length = q.method.message_count
    connection.close()
    return queue_length

def log_scaling(queue_len, λ, required, active):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([queue_len, round(λ, 2), required, active])

def adjust_workers():
    global current_workers, last_queue_length

    current_queue_length = get_queue_length()
    new_messages = max(0, current_queue_length - last_queue_length)
    λ = new_messages / CHECK_INTERVAL
    required_workers = max(1, math.ceil((λ * T) / C))

    print(f"[Supervisor] λ={λ:.2f} msg/s | Requiere: {required_workers} | Activos: {len(current_workers)}")

    # Escalado
    diff = required_workers - len(current_workers)
    if diff > 0:
        for _ in range(diff):
            p = multiprocessing.Process(target=insult_service)
            p.start()
            current_workers.append(p)
            print("[Supervisor] +1 Worker lanzado")
    elif diff < 0:
        for _ in range(-diff):
            if len(current_workers) > 1:
                p = current_workers.pop()
                p.terminate()
                print("[Supervisor] -1 Worker detenido")

    # Logging
    log_scaling(current_queue_length, λ, required_workers, len(current_workers))

    last_queue_length = current_queue_length

if __name__ == "__main__":
    last_queue_length = get_queue_length()
    while True:
        adjust_workers()
        time.sleep(CHECK_INTERVAL)
