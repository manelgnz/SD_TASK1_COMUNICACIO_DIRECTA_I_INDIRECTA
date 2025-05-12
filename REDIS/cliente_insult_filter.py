import redis
import time
import random

client = redis.Redis(host='localhost', port=6379, db=0)

NUM_MESSAGES = 20000
queue_name = "task_queue"
filtered_list = "filtered_messages"

# Llista d'insults hardcodeada
insults = ["idiota", "tonto", "imbècil", "burro", "cap de suro",
           "mal educat", "bàrbar", "malparit", "ruc", "dropo"]

# Esborrem dades antigues
client.delete(queue_name)
client.delete(filtered_list)

# Enviar missatges
start_time = time.time()

for i in range(NUM_MESSAGES):
    if i % 2 == 0:
        message = f"Missatge normal número {i+1}"
    else:
        message = random.choice(insults)
    client.rpush(queue_name, message)
    print(f"Enviat: {message}")

# Esperem a que el worker filtri tot
print("\n⏳ Esperant que el worker filtri tots els missatges...")

while True:
    filtered_count = client.llen(filtered_list)
    if filtered_count >= NUM_MESSAGES:
        break
    time.sleep(0.1)  # Espera petita per no saturar Redis

end_time = time.time()
durada = end_time - start_time

print(f"\n✅ Tots els missatges filtrats en {durada:.3f} segons.")
