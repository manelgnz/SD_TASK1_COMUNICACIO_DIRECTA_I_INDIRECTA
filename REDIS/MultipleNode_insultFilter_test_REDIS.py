import redis
import time
import multiprocessing
from InsultFilter_REDIS import send_text_for_filtering, get_filtered_results, filter_worker

def start_worker():
    filter_worker()  # Entra en bucle infinito

def run_test(num_workers, num_messages):
    print(f"\n🚀 Test con {num_workers} worker(s) y {num_messages} mensajes")

    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Limpia colas y resultados
    redis_client.delete("text_queue")
    redis_client.delete("filtered_results")
    redis_client.delete("insult_list")

    # Asegura que los insultos están en formato set
    redis_client.sadd("insult_list", "Noob", "You're a fool!", "Clown", "You fight like a dairy farmer!")

    # Inicia workers como procesos separados
    workers = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=start_worker, daemon=True)
        p.start()
        workers.append(p)

    time.sleep(1)  # Da tiempo para que arranquen los workers

    # Genera y envía mensajes
    for i in range(num_messages):
        insult = "Noob" if i % 2 == 0 else "Hello my friend"
        msg = f"Message #{i}: {insult}"
        send_text_for_filtering(msg)

    # Espera a que se procesen todos los mensajes
    start = time.time()
    while len(get_filtered_results()) < num_messages:
        time.sleep(0.2)
    end = time.time()

    total_time = end - start
    avg_time = total_time / num_messages
    throughput = num_messages / total_time

    print(f"✅ Tiempo total: {total_time:.2f} segundos")
    print(f"📊 Tiempo promedio por mensaje: {avg_time:.4f} s")
    print(f"⚡ Throughput: {throughput:.2f} mensajes/segundo")

    # Finaliza los workers
    for p in workers:
        p.terminate()
        p.join()

    return total_time

if __name__ == "__main__":
    num_messages = 3000
    tiempos = {}

    for workers in range(1, 4):
        tiempo = run_test(num_workers=workers, num_messages=num_messages)
        tiempos[workers] = tiempo

    # Calcular speedup entre 1 y 3 workers
    if 1 in tiempos and 3 in tiempos:
        speedup = tiempos[1] / tiempos[3]
        print(f"\n🚀 REDIS SPEEDUP(3 workers): {speedup:.2f}x")
