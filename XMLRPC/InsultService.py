import redis
import random
import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import argparse  # Para manejar argumentos de línea de comandos

class InsultService:
    def __init__(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        self.subscribers = []
        print("[InsultService] Initialized with Redis backend and no subscribers.")

    def add_insult(self, insult):
        if not self.redis_client.sismember("insults", insult):
            self.redis_client.sadd("insults", insult)
            print(f"[InsultService] Added insult: {insult}")
            return True
        print(f"[InsultService] Insult '{insult}' already exists.")
        return False

    def get_insults(self):
        insults = list(self.redis_client.smembers("insults"))
        print(f"[InsultService] Returning insults: {insults}")
        return insults

    def subscribe(self, callback_url):
        if callback_url not in self.subscribers:
            self.subscribers.append(callback_url)
            print(f"[InsultService] New subscriber added: {callback_url}")
            return True
        print(f"[InsultService] Subscriber '{callback_url}' is already registered.")
        return False

    def broadcast_insults(self):
        print("[InsultService] Starting insult broadcasting...")
        while True:
            if self.subscribers and self.redis_client.scard("insults") > 0:
                random_insult = random.choice(list(self.redis_client.smembers("insults")))
                for subscriber in self.subscribers:
                    try:
                        subscriber_proxy = xmlrpc.client.ServerProxy(subscriber)
                        response = subscriber_proxy.receive_insult(random_insult)
                        print(f"[InsultService] Sent insult '{random_insult}' to {subscriber}. Response: {response}")
                    except Exception as e:
                        print(f"[InsultService] Error broadcasting insult to {subscriber}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Start an InsultService node.")
    parser.add_argument("--port", type=int, default=8000, help="Port number for the InsultService")
    args = parser.parse_args()

    # Usar el puerto especificado
    server = SimpleXMLRPCServer(("localhost", args.port), allow_none=True)
    service = InsultService()

    server.register_function(service.add_insult, "add_insult")
    server.register_function(service.get_insults, "get_insults")
    server.register_function(service.subscribe, "subscribe")

    threading.Thread(target=service.broadcast_insults, daemon=True).start()

    try:
        print(f"[InsultService] InsultService is running on port {args.port}...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("[InsultService] Shutting down InsultService...")
        server.server_close()