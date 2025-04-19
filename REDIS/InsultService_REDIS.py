import random
import time
import redis
import threading

class InsultService:
    def __init__(self):
        # Configuración de Redis
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.insult_key = 'insult_list'  # Lista donde se almacenan los insultos
        self.insult_set_key = 'insult_set'  # Set donde se almacenan los insultos únicos
        self.channel = 'insult_channel'  # Canal para transmisión
        self.lock = threading.Lock()  # Bloqueo para evitar condiciones de carrera

    def add_insult(self, insult: str):
        with self.lock:
            # Agregar al set para contar únicos
            self.r.sadd(self.insult_set_key, insult)
            # Agregar a la lista con rpush
            self.r.rpush(self.insult_key, insult)

    def get_insults(self):
        return self.r.lrange(self.insult_key, 0, -1)  # Obtener todos los insultos de la lista

    def broadcast_insults(self):
        def publish():
            while True:
                insults = self.get_insults()
                if insults:
                    insult = random.choice(insults)
                    self.r.publish(self.channel, insult)
                time.sleep(5)

        thread = threading.Thread(target=publish, daemon=True)
        thread.start()


if __name__ == '__main__':
    service = InsultService()
    service.add_insult("You fight like a dairy farmer!")
    service.add_insult("You're as bright as a black hole.")
    print("Insults:", service.get_insults())
    service.broadcast_insults()

    while True:
        time.sleep(1)
