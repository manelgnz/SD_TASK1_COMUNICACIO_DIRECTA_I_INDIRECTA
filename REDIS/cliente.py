import redis
import time
import threading

client = redis.Redis(host='localhost', port=6379, db=0)

NUM_INSULTS = 5000
queue_name = "task_queue"
processed_list = "insultList"

# Funció que escolta insults des de la cua de broadcast i els imprimeix
def escoltar_broadcast():
    broadcast_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    print("\n🎧 Escoltant insults broadcast...")

    while True:
        msg = broadcast_client.blpop("broadcast_queue", timeout=0)
        if msg:
            print(f"[Broadcast rebut] {msg[1]}")

# Llança el thread per escoltar broadcast en paral·lel
threading.Thread(target=escoltar_broadcast, daemon=True).start()

# Limpiar la cola y la lista de procesados
client.delete(queue_name)
client.delete(processed_list)

# Enviar los insultos
start_time = time.time()

for i in range(NUM_INSULTS):
    insulto = f"Insulto #{i+1}..."
    client.rpush(queue_name, insulto)
    print(f"Produced: {insulto}")

# Esperar hasta que el worker haya procesado todos
print("\nEsperando a que el worker procese todos los mensajes...")

while True:
    processed_count = client.llen(processed_list)
    if processed_count >= NUM_INSULTS:
        break

end_time = time.time()
duracion_total = end_time - start_time

print(f"\n✅ {NUM_INSULTS} mensajes fueron procesados en {duracion_total:.3f} segundos.")
