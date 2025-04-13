import redis
import time
import threading
import random

class InsultService:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.insult_key = 'insult_list'
        self.channel = 'insult_channel'
        self.lock = threading.Lock()

    def add_insult(self, insult: str):
        with self.lock:
            insults = self.r.lrange(self.insult_key, 0, -1)
            if insult not in insults:
                self.r.rpush(self.insult_key, insult)

    def get_insults(self):
        return self.r.lrange(self.insult_key, 0, -1)

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
