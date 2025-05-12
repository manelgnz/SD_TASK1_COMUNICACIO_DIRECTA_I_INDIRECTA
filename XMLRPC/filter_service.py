from xmlrpc.server import SimpleXMLRPCServer
from threading import Lock
import xmlrpc.client

class InsultFilterService:
    def __init__(self, port, insult_service_url):
        self.port = port
        self.filtered_results = []  # Llista de textos filtats
        self.lock = Lock()  # Control d'accés concurrent
        self.insult_service = xmlrpc.client.ServerProxy(insult_service_url)
        
        # Iniciar servidor RPC
        self.server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
        self.server.register_instance(self)
        
        print(f"🛡️  InsultFilterService iniciat a http://localhost:{port}")
        print(f"🔗 Connectat a InsultService: {insult_service_url}")

    def filter_text(self, text):
        """Filtra insults en un text i l'emmagatzema."""
        try:
            # Obtenir insults actuals del servei principal
            insults = self.insult_service.get_insults()
            filtered_text = text
            
            # Reemplaçar cada insult per "CENSORED"
            for insult in insults:
                filtered_text = filtered_text.replace(insult, "CENSORED")
            
            # Guardar el resultat
            with self.lock:
                self.filtered_results.append(filtered_text)
                print(f"✅ Text filtrat: {filtered_text[:50]}...")
            
            return filtered_text
        
        except Exception as e:
            print(f"❌ Error filtrant text: {e}")
            return "Error en el filtre"

    def get_filtered_results(self):
        """Retorna tots els textos filtats."""
        with self.lock:
            return self.filtered_results.copy()

    def stop(self):
        """Atura el servei."""
        self.server.server_close()
        print("🛑 InsultFilterService aturat")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Ús: python filter_service.py <port> <insult_service_url>")
        sys.exit(1)

    port = int(sys.argv[1])
    insult_service_url = sys.argv[2]
    
    filter_service = InsultFilterService(port, insult_service_url)
    
    try:
        print("⏳ Filtre actiu. Premeu Ctrl+C per aturar.")
        filter_service.server.serve_forever()
    except KeyboardInterrupt:
        filter_service.stop()