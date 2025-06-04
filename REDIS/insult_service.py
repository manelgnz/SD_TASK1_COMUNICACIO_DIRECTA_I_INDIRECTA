import redis
import multiprocessing
import os
import random
import time

# Connexió i estructures de Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_NAME = "task_queue"
LIST_NAME = "insultList"
SET_NAME = "insultSet"

# Llista hardcodejada d'insults per fer broadcast
INSULTS = [
    "Ets més lent que un cargol amb ressaca",
    "Tens el carisma d'una sabata vella",
    "Parles i m'adormo",
    "Ets com una versió beta: inestable i incomplet",
    "Tens menys gràcia que una fotocòpia borrosa",
    "Ets tan original com un mem reciclat",
    "Si fossis més lent, aniries enrere",
    "Tens menys llum que un llum trencat",
    "El teu talent és com un unicorn: no existeix",
    "Ets tan confús com un tutorial en xinès"
]

# Funció per als workers
def worker_process(worker_id):
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    print(f"[{worker_id}] Procés iniciat.")

    while True:
        task = client.blpop(QUEUE_NAME, timeout=5)
        if task:
            insult = task[1]
            if not client.sismember(SET_NAME, insult):
                pipe = client.pipeline()
                pipe.rpush(LIST_NAME, insult)
                pipe.sadd(SET_NAME, insult)
                pipe.execute()
                print(f"[{worker_id}] Afegeix insult: {insult}")
            else:
                print(f"[{worker_id}] L'insult ja existeix: {insult}")
        else:
            print(f"[{worker_id}] Esperant tasques...")

# Funció que envia un insult aleatori cada 5 segons
def insult_broadcaster():
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    while True:
        insult = random.choice(INSULTS)
        client.rpush(QUEUE_NAME, insult)
        print(f"[Broadcast] Enviat insult aleatori: {insult}")
        time.sleep(5)

# Inici principal
if __name__ == "__main__":
    num_workers = 1

    print(f"Inicialitzant {num_workers} workers i un broadcaster...")

    # Netejar Redis
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    client.delete(QUEUE_NAME)
    client.delete(LIST_NAME)
    client.delete(SET_NAME)

    processes = []

    # Llençar els workers
    for i in range(num_workers):
        p = multiprocessing.Process(target=worker_process, args=(f"worker-{i+1}",))
        p.start()
        processes.append(p)

    # Llençar el broadcaster
    b = multiprocessing.Process(target=insult_broadcaster)
    b.start()
    processes.append(b)

    # Esperar tots els processos
    for p in processes:
        p.join()
