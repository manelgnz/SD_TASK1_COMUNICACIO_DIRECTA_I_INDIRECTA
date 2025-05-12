from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from threading import Thread, Lock
import redis
import random
import time
import pickle

class InsultService:
    def __init__(self, port, redis_host='localhost', redis_port=6379):
        self.port = port
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.subscribers = set()
        self.lock = Lock()
        self.running = True

        if self.redis.exists("insults"):
            tipo = self.redis.type("insults").decode()
            if tipo != "list":
                self.redis.delete("insults")  # Elimina la clau si no és una llista

        if not self.redis.exists("insults"):
            self.redis.rpush("insults", *[
                "Ets més lent que un cargol amb ressaca.",
                "Tens menys gràcia que un error de compilació.",
                "Ni l'IA et vol ajudar."
            ])


        # Iniciar broadcaster
        self.broadcaster = Thread(target=self._broadcast_insults)
        self.broadcaster.start()

        # Configurar servidor RPC
        self.server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
        self.server.register_instance(self)
        print(f"🔥 InsultService (Redis) en puerto {port}")

    def _broadcast_insults(self):
        """Envía insults aleatorios cada 5 segundos a suscriptores"""
        while self.running:
            time.sleep(5)
            insult = self.generate_insult()
            for callback in list(self.subscribers):
                try:
                    callback(insult)
                except:
                    self.subscribers.remove(callback)

    # --- Métodos RPC ---
    def generate_insult(self):
        """Devuelve un insulto aleatorio desde Redis"""
        return self.redis.lindex("insults", random.randint(0, self.redis.llen("insults")-1)).decode()

    def add_insult(self, insult):
        """Añade un insulto a la lista compartida"""
        if not self.redis.lrem("insults", 0, insult):  # Si no existe
            self.redis.rpush("insults", insult)
            return True
        return False

    def get_insults(self):
        """Devuelve todos los insults"""
        return [i.decode() for i in self.redis.lrange("insults", 0, -1)]

    def subscribe(self, callback_url):
        """Registra un suscriptor"""
        self.subscribers.add(xmlrpc.client.ServerProxy(callback_url))
        return True

    def stop(self):
        """Detiene el servicio"""
        self.running = False
        self.server.server_close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    service = InsultService(port)
    try:
        service.server.serve_forever()
    except KeyboardInterrupt:
        service.stop()