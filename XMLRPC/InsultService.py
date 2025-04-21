import random
import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client

class InsultService:
    def __init__(self):
        self.insults = []
        self.subscribers = []

    def add_insult(self, insult):
        if insult not in self.insults:
            self.insults.append(insult)
            return True
        return False

    def get_insults(self):
        return self.insults

    def subscribe(self, callback_url):
        if callback_url not in self.subscribers:
            self.subscribers.append(callback_url)
            return True
        return False

    def broadcast_insults(self):
        while True:
            if self.subscribers and self.insults:
                random_insult = random.choice(self.insults)
                for subscriber in self.subscribers:
                    try:
                        subscriber_proxy = xmlrpc.client.ServerProxy(subscriber)
                        response = subscriber_proxy.receive_insult(random_insult)
                        print(f"Insult '{random_insult}' sent to {subscriber} with response: {response}")
                    except Exception as e:
                        print(f"Error broadcasting insult to {subscriber}: {e}")
            time.sleep(5)

# Only run the server if this file is executed directly
if __name__ == "__main__":
    # XML-RPC server setup
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    service = InsultService()

    server.register_function(service.add_insult, "add_insult")
    server.register_function(service.get_insults, "get_insults")
    server.register_function(service.subscribe, "subscribe")

    # Start broadcasting insults in a separate thread
    threading.Thread(target=service.broadcast_insults, daemon=True).start()

    try:
        print("InsultService is running on port 8000...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down InsultService...")
        server.server_close()