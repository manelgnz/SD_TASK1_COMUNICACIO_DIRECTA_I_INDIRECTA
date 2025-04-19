import Pyro4
import threading
import re

@Pyro4.expose
class InsultFilterService(object):
    def __init__(self):
        self.results = []
        self.insults = [
            "You are a fool",
            "Your brain is like a sieve",
            "Get a life",
            "You're a genius, just kidding!"
        ]
        self.lock = threading.Lock()
        print("[INIT] InsultFilterService initialized.")

    def filter_text(self, text):
        print(f"[FILTER] Received text to filter: '{text}'")
        filtered_text = text
        for insult in self.insults:
            # Using regular expressions for better matching (case-insensitive, word boundaries)
            pattern = r'\b' + re.escape(insult) + r'\b'
            filtered_text = re.sub(pattern, "CENSORED", filtered_text, flags=re.IGNORECASE)
        
        with self.lock:
            self.results.append(filtered_text)
            print(f"[FILTER] Filtered text saved: '{filtered_text}'")

        return filtered_text

    def get_filtered_results(self):
        print("[RESULTS] Returning filtered results list.")
        return self.results


def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    filter_service = InsultFilterService()

    uri = daemon.register(filter_service)
    ns.register("InsultFilterService", uri)

    print(f"[MAIN] InsultFilterService is ready. URI: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
