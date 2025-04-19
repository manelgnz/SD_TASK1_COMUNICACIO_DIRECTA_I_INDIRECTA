import Pyro4
import threading
import time
import random

# Global list of insults
insults = [
    "You are a fool",
    "Your brain is like a sieve",
    "Get a life",
    "You're a genius, just kidding!"
]

@Pyro4.expose
class InsultService(object):
    def __init__(self):
        self.subscribers = []
        print("[INIT] InsultService initialized.")

    def add_insult(self, insult):
        """Add an insult if it's not already in the list."""
        if insult not in insults:
            insults.append(insult)
            print(f"[ADD] Added insult: {insult}")
            return True
        print(f"[ADD] Insult already exists: {insult}")
        return False

    def get_insults(self):
        """Retrieve the current list of insults."""
        print(f"[GET] Current insults list requested: {insults}")
        return insults

    def subscribe(self, subscriber_uri):
        """Add a new subscriber to receive insults."""
        try:
            subscriber = Pyro4.Proxy(subscriber_uri)
            self.subscribers.append(subscriber)
            print(f"[SUBSCRIBE] New subscriber registered: {subscriber}")
        except Exception as e:
            print(f"[SUBSCRIBE] Failed to register subscriber: {e}")

    def unsubscribe(self, subscriber_uri):
        """Unsubscribe a subscriber."""
        self.subscribers = [s for s in self.subscribers if s._pyroUri != subscriber_uri]
        print(f"[UNSUBSCRIBE] Subscriber removed: {subscriber_uri}")

    def broadcast_insults(self):
        """Broadcast a random insult to subscribers every 5 seconds."""
        while True:
            time.sleep(5)
            if not insults:
                print("[BROADCAST] No insults to broadcast.")
                continue
            insult = random.choice(insults)
            print(f"[BROADCAST] Broadcasting insult: {insult}")
            self.broadcast(insult)

    def broadcast(self, insult):
        """Notify all subscribers about a new insult."""
        for subscriber in self.subscribers:
            try:
                print(f"[BROADCAST] Notifying subscriber: {subscriber}")
                subscriber.notify(insult)
            except Exception as e:
                print(f"[BROADCAST] Failed to notify subscriber: {e}")

def main():
    # Set up Pyro daemon and name server
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    insult_service = InsultService()

    # Register the service with Pyro name server
    uri = daemon.register(insult_service)
    ns.register("InsultService", uri)

    # Start the broadcasting thread
    broadcaster_thread = threading.Thread(target=insult_service.broadcast_insults)
    broadcaster_thread.daemon = True
    broadcaster_thread.start()

    print(f"[MAIN] InsultService is ready. URI: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
