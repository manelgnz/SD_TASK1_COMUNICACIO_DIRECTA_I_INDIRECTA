import time
import multiprocessing
import matplotlib.pyplot as plt
from insult_filter_redis import InsultFilter

NUM_MESSAGES = 10000

# 👇 ESTA función debe estar en el nivel superior (¡no anidada!)
def run_filter_worker():
    service = InsultFilter()
    service.start_worker()
    while True:
        time.sleep(1)

def stress_test_with_workers(num_workers):
    print(f"\n=== Ejecutando test con {num_workers} worker(s) ===")

    # Limpiar Redis antes de iniciar
    r = InsultFilter().r
    r.delete('filter_queue')
    r.delete('filtered_results')

    # Lanzar workers
    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=run_filter_worker)
        p.start()
        processes.append(p)

    time.sleep(1)  # Dar tiempo a que arranquen

    # Enviar textos
    service = InsultFilter()
    for i in range(NUM_MESSAGES):
        service.add_text(f"This is message #{i} with some insult")

    # Esperar a que todos los textos se procesen
    start = time.time()
    while True:
        processed = len(service.get_results())
        if processed >= NUM_MESSAGES:
            break
        time.sleep(0.05)
    end = time.time()

    # Finalizar workers
    for p in processes:
        p.terminate()
        p.join()

    total_time = end - start
    print(f"✅ Mensajes procesados: {NUM_MESSAGES}")
    print(f"⏱️ Tiempo total: {total_time:.2f} s")
    print(f"⚡️ Throughput: {NUM_MESSAGES / total_time:.2f} msgs/sec")
    return total_time

def run_tests_and_plot():
    results = {}
    worker_counts = [1, 2, 3, 4]

    for n in worker_counts:
        t = stress_test_with_workers(n)
        results[n] = t

    # Calcular speedups
    base_time = results[1]
    speedups = [base_time / results[n] for n in worker_counts]

    # Graficar
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.plot(worker_counts, [results[n] for n in worker_counts], marker='o')
    plt.title("Tiempo total vs Número de workers")
    plt.xlabel("Workers")
    plt.ylabel("Tiempo (s)")

    plt.subplot(1, 2, 2)
    plt.plot(worker_counts, speedups, marker='o', color='green')
    plt.title("Speedup vs Número de workers")
    plt.xlabel("Workers")
    plt.ylabel("Speedup")

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')  # Necesario en Windows
    run_tests_and_plot()
