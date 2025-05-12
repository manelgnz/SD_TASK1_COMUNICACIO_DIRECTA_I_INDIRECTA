import redis
import multiprocessing
import os

# Paràmetres de connexió Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_NAME = "task_queue"
FILTERED_LIST = "filtered_messages"

# Llista hardcoded d'insults
INSULTS = [
    "idiota", "tonto", "imbècil", "burro", "cap de suro",
    "mal educat", "bàrbar", "malparit", "ruc", "dropo"
]

def worker_process(worker_id):
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    print(f"[{worker_id}] Worker iniciat (PID: {os.getpid()})")

    while True:
        task = client.blpop(QUEUE_NAME, timeout=5)
        if task:
            message = task[1]
            if message in INSULTS:
                client.rpush(FILTERED_LIST, "CENSORED")
                print(f"[{worker_id}] 🛑 Missatge censurat: {message}")
            else:
                client.rpush(FILTERED_LIST, message)
                print(f"[{worker_id}] ✅ Missatge net: {message}")
        else:
            print(f"[{worker_id}] Esperant nous missatges...")

if __name__ == "__main__":
    num_workers = 2  # ← Pots canviar aquest valor per escalar més

    print(f"🚀 Iniciant {num_workers} workers...")

    # Crear i iniciar processos workers
    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=worker_process, args=(f"worker-{i+1}",))
        p.start()
        processes.append(p)

    # Esperar que acabin (opcional, es pot interrompre amb Ctrl+C)
    for p in processes:
        p.join()
