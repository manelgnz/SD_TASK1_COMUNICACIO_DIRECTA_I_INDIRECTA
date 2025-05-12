from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from threading import Thread, Lock
import random
import time

class InsultService:
    def __init__(self, port):
        self.port = port
        self.insults = [
            "Ets més lent que un cargol amb ressaca.",
            "Tens menys gràcia que un error de compilació.",
            "Ni l'IA et vol ajudar."
        ]
        self.subscribers = set()
        self.lock = Lock()
        self.running = True

        # Iniciar broadcast automàtic
        self.broadcaster = Thread(target=self._broadcast_insults)
        self.broadcaster.daemon = True
        self.broadcaster.start()

        # Configurar servidor
        self.server = SimpleXMLRPCServer(("localhost", self.port), allow_none=True)
        self.server.register_introspection_functions()
        self.server.register_instance(self)
        
        print(f"🔥 InsultService iniciat a http://localhost:{self.port}")
        print(f"📜 Insults inicials: {len(self.insults)}")
        print("🔄 Broadcast actiu cada 5 segons")

    def _broadcast_insults(self):
        """Envia insults aleatoris als subscriptors cada 5 segons"""
        while self.running:
            time.sleep(5)
            with self.lock:
                if self.insults and self.subscribers:
                    insult = random.choice(self.insults)
                    for callback in list(self.subscribers):
                        try:
                            callback(insult)
                            print(f"📢 Enviat: {insult[:20]}... a {callback}")
                        except Exception as e:
                            print(f"❌ Error enviant a {callback}: {e}")
                            self.subscribers.remove(callback)

    def generate_insult(self):
        """Genera un insult aleatori (compatibilitat amb worker original)"""
        with self.lock:
            insult = random.choice(self.insults)
            print(f"🎲 Generat: {insult}")
            return insult

    def add_insult(self, new_insult):
        """Afegeix un nou insult si no existeix"""
        with self.lock:
            if new_insult not in self.insults:
                self.insults.append(new_insult)
                print(f"➕ Afegit: {new_insult}")
                return True
            print(f"⏭ Duplicat: {new_insult}")
            return False

    def get_insults(self):
        """Retorna tots els insults"""
        with self.lock:
            return self.insults.copy()

    def subscribe(self, callback_url):
        """Afegeix un nou subscriptor"""
        with self.lock:
            try:
                callback = xmlrpc.client.ServerProxy(callback_url)
                self.subscribers.add(callback)
                print(f"🎯 Subscriptor afegit: {callback_url}")
                return True
            except Exception as e:
                print(f"❌ Error subscriptor {callback_url}: {e}")
                return False

    def unsubscribe(self, callback_url):
        """Elimina un subscriptor"""
        with self.lock:
            for sub in list(self.subscribers):
                if str(sub) == callback_url:
                    self.subscribers.remove(sub)
                    print(f"🚫 Subscriptor eliminat: {callback_url}")
                    return True
            return False

    def stop(self):
        """Atura el servei"""
        self.running = False
        self.server.server_close()
        print("🛑 Servei aturat")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Ús: python insult_service.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    service = InsultService(port)
    
    try:
        print("⏳ Premeu Ctrl+C per aturar\n")
        service.server.serve_forever()
    except KeyboardInterrupt:
        service.stop()