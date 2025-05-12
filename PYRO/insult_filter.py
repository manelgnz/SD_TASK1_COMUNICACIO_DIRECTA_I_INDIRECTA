# insult_filter.py
import Pyro4
import sys

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultFilter:
    def __init__(self, insults):
        self.insults = insults
        self.results = []

    def filter_text(self, text):
        filtered = text
        for insult in self.insults:
            filtered = filtered.replace(insult, "CENSURAT")
        self.results.append(filtered)
        return filtered

    def get_results(self):
        return self.results

def main():
    if len(sys.argv) != 2:
        print("Ús: python insult_filter.py <nom_del_filter>")
        sys.exit(1)

    name = sys.argv[1]

    ns = Pyro4.locateNS()
    daemon = Pyro4.Daemon()
    
    # Aquest és un exemple, però potser després et convé que els insults vinguin d'un altre servei
    shared_insults = ["idiota", "burro", "tonto"]

    filter_obj = InsultFilter(shared_insults)
    uri = daemon.register(filter_obj)
    ns.register(name, uri)

    print(f"✅ Filtre '{name}' registrat.")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
