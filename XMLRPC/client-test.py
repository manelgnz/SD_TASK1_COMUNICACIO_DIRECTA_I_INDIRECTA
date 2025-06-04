import xmlrpc.client
import multiprocessing
import time
import random
import csv
import os

# Configuració
service_urls = [
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:8002"
]

num_peticions_totals = 20
num_processes = len(service_urls)
CSV_FILENAME = "resultats_test.csv"

print("\n=== 🚀 INICIANT CLIENT AMB BALANÇ DE CARREGA ===")
print(f"🔢 Total de peticions: {num_peticions_totals}")
print(f"🖥️  Serveis disponibles: {len(service_urls)}")
print(f"⚙️  Utilitzant {num_processes} processos paral·lels")

# Comptador global
peticion_counter = multiprocessing.Value('i', 0)
counter_lock = multiprocessing.Lock()

def get_random_service():
    return random.choice(service_urls)

def enviar_peticions(process_id, num_peticions, result_queue):
    results = []
    
    for i in range(num_peticions):
        service_url = get_random_service()
        proxy = xmlrpc.client.ServerProxy(service_url, allow_none=True)
        
        try:
            insult = proxy.generate_insult()
            with counter_lock:
                peticion_counter.value += 1
            results.append(("OK", True))
        except Exception as e:
            with counter_lock:
                peticion_counter.value += 1
            results.append(("Error", False))

    result_queue.put((process_id, results))

def init_csv_file():
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Nombre de workers',
                'Nombre de peticions',
                'Temps total (s)'
            ])

def save_results(num_workers, total_peticiones, temps_total):
    with open(CSV_FILENAME, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            num_workers,
            total_peticiones,
            f"{temps_total:.3f}"
        ])

if __name__ == '__main__':
    init_csv_file()
    
    peticions_per_process = num_peticions_totals // num_processes
    processes = []
    result_queue = multiprocessing.Queue()

    print(f"📊 Peticions per procés: ~{peticions_per_process}")
    print("⏳ Iniciant proves...\n")

    start_time = time.time()

    # Llançar processos
    for p_id in range(num_processes):
        p = multiprocessing.Process(
            target=enviar_peticions,
            args=(p_id, peticions_per_process, result_queue)
        )
        processes.append(p)
        p.start()
        print(f"🔄 Procés {p_id} llançat")

    # Esperar finalització
    print("\n⏳ Esperant finalització de processos...")
    for p in processes:
        p.join()

    # Comptar resultats
    exit = 0
    errors = 0
    while not result_queue.empty():
        _, process_results = result_queue.get()
        for _, status in process_results:
            if status:
                exit += 1
            else:
                errors += 1

    end_time = time.time()
    total_time = end_time - start_time

    # Guardar resultats en CSV
    save_results(
        num_workers=num_processes,
        total_peticiones=num_peticions_totals,
        temps_total=total_time
    )

    print("\n=== 📝 RESUM FINAL ===")
    print(f"Nombre de workers: {num_processes}")
    print(f"Nombre de peticions: {num_peticions_totals}")
    print(f"Temps total (s): {total_time:.3f}")
    print(f"\n📊 Resultats guardats a '{CSV_FILENAME}'")
    print("\n🏁 Proves completades")