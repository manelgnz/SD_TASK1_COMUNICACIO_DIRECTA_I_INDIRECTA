import Pyro4
import multiprocessing
import time
import sys
import csv
import os

NUM_PETICIONS = 30000
CSV_FILENAME = "resultats_test.csv"

@Pyro4.expose
class DummyClient:
    def receive_insult(self, insult):
        print(f"Rebut insult: {insult}")

def enviar_peticions(worker_name, peticions_per_process):
    ns = Pyro4.locateNS()
    worker = Pyro4.Proxy(ns.lookup(worker_name))

    for _ in range(peticions_per_process):
        insult = worker.generate_insult()
        print(f"[PETICIÓ - {worker_name}] {insult}")

def main():
    ns = Pyro4.locateNS()
    daemon = Pyro4.Daemon()

    dummy_client = DummyClient()
    uri = daemon.register(dummy_client)
    proxy = Pyro4.Proxy(uri)

    # Obtenir la llista de noms de workers registrats
    all_registered = ns.list(prefix="worker.")
    WORKER_NAMES = list(all_registered.keys())
    NUM_PROCESSES = len(WORKER_NAMES)

    if NUM_PROCESSES == 0:
        print("[ERROR] No s'han trobat workers registrats amb prefix 'worker.'")
        sys.exit(1)

    workers = [Pyro4.Proxy(ns.lookup(name)) for name in WORKER_NAMES]

    for worker in workers:
        resposta = worker.subscribe(proxy)
        print(f"[CLIENT] Subscric a {worker._pyroUri}: {resposta}")

    print(f"Iniciant test amb {NUM_PETICIONS} peticions i {NUM_PROCESSES} processos...")

    peticions_per_process = NUM_PETICIONS // NUM_PROCESSES
    processes = []

    t0 = time.time()

    for i in range(NUM_PROCESSES):
        worker_name = WORKER_NAMES[i]
        p = multiprocessing.Process(target=enviar_peticions, args=(worker_name, peticions_per_process))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    t1 = time.time()
    total_global = round(t1 - t0, 3)
    print(f"Temps total: {total_global}s per {NUM_PETICIONS} peticions")

    # Guardar resultats al .csv
    file_exists = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Nombre de workers", "Nombre de peticions", "Temps total (s)"])
        writer.writerow([NUM_PROCESSES, NUM_PETICIONS, total_global])


    print(f"[CSV] Resultats guardats a '{CSV_FILENAME}'")

    time.sleep(2)
    print("[CLIENT] Test finalitzat. Tancant daemon.")
    daemon.shutdown()
    sys.exit(0)

if __name__ == "__main__":
    main()
