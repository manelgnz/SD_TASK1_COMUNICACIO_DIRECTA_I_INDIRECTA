import Pyro4
import multiprocessing
import time
import random
import sys

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultService:
    def __init__(self, name):
        self.name = name
        self.insults = [
            "Ets més lent que un pingüí coix.",
            "Programaries millor amb un pal i una pedra.",
            "El teu cervell fa timeout."
        ]
        self.subscribers = multiprocessing.Manager().list()
        self._start_broadcast_process()

    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            return f"Insult afegit: '{insult}'"
        else:
            return "Insult ja existent."

    def generate_insult(self):
        if self.insults:
            insult = random.choice(self.insults)
            print(f"[WORKER] Insult generat: {insult}")
            return insult
        else:
            return "Cap insult disponible."

    def get_insults(self):
        return self.insults

    def subscribe(self, callback):
        if callback not in self.subscribers:
            self.subscribers.append(callback)
            print(f"[WORKER] Nova subscripció: {callback._pyroUri}")
            return f"Subscric {callback._pyroUri}"
        print(f"[WORKER] Ja subscrit: {callback._pyroUri}")
        return "Ja subscrit."

    def _start_broadcast_process(self):
        p = multiprocessing.Process(target=self._broadcast_loop, daemon=True)
        p.start()

    def _broadcast_loop(self):
        while True:
            if self.subscribers and self.insults:
                insult = random.choice(self.insults)
                for subscriber in list(self.subscribers):
                    try:
                        print(f"[WORKER] Enviant insult a {subscriber._pyroUri}: {insult}")
                        subscriber.receive_insult(f"[{self.name}] {insult}")
                    except Pyro4.errors.CommunicationError:
                        print(f"[WORKER] Error comunicant amb {subscriber._pyroUri}")
                        continue
            time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Ús: python worker.py <nom_worker>")
        sys.exit(1)

    worker_name = sys.argv[1]
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(InsultService(worker_name))
    ns.register(worker_name, uri)

    print(f"✅ Worker '{worker_name}' registrat.")
    daemon.requestLoop()
