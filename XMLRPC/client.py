import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import threading

# Mètode per rebre insults del broadcast
def receive_insult(insult):
    print(f"[Client] Insult rebut del broadcast: {insult}")
    return f"Insult rebut: {insult}"

# Configurar un servidor XML-RPC dins del client per rebre el broadcast
def start_client_server():
    server = SimpleXMLRPCServer(("localhost", 9000), allow_none=True)
    server.register_function(receive_insult, "receive_insult")
    print("[Client] Servidor del client escoltant al port 9000 per rebre insults...")
    server.serve_forever()

# Iniciar el servidor del client en un fil separat
threading.Thread(target=start_client_server, daemon=True).start()

# Connectar amb InsultService
insult_service = xmlrpc.client.ServerProxy("http://localhost:8000/")

# Afegir insults a InsultService
print("Afegint insults a InsultService...")
insult_service.add_insult("idiot")
insult_service.add_insult("stupid")
insult_service.add_insult("fool")
print("Insults actuals:", insult_service.get_insults())

# Subscriure's al broadcaster d'insults amb la URL del client
insult_service.subscribe("http://localhost:9000/")

# Connectar amb InsultFilter
insult_filter = xmlrpc.client.ServerProxy("http://localhost:8001/")

# Configurar insults a InsultFilter
print("Configurant insults a InsultFilter...")
insult_filter.set_insults(insult_service.get_insults())

# Filtrar textos
print("Filtrant textos...")
filtered_text1 = insult_filter.filter_text("You are an idiot!")
filtered_text2 = insult_filter.filter_text("This is a stupid idea.")
filtered_text3 = insult_filter.filter_text("No insults here.")
print("Textos filtrats:", insult_filter.get_filtered_results())

# Recuperar textos filtrats
print("Recuperant tots els textos filtrats...")
print(insult_filter.get_filtered_results())

# Mantenir el client actiu per rebre insults del broadcast
print("[Client] Esperant insults del broadcast. Prem Ctrl+C per sortir.")
try:
    while True:
        pass  # Espera infinita per mantenir el procés actiu
except KeyboardInterrupt:
    print("[Client] Tancant el client...")