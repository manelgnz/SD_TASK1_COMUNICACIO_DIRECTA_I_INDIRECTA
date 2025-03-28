import redis
import time
import threading
import random

class InsultService:
    def __init__(self, host="localhost", port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.channel_name = "insult_channel"
        self.insult_list_name = "insultList"  # Nom llista insults

    def add_insult(self, insult):  
        insults = self.client.lrange(self.insult_list_name, 0, -1)  # Obtenir llista insults
        if insult not in insults:  
            self.client.rpush(self.insult_list_name, insult)  # Afegim insult a Redis
            print(f"Nou insult afegit: {insult}")

    def get_insults(self): 
        return self.client.lrange(self.insult_list_name, 0, -1)  

    def broadcast_insults(self):  # Publica insults aleatoris cada 5 segons.
        while True:
            insults = self.get_insults()  # Obtenim llista insults
            if insults:  # Comprovem si hi ha insults a la llista
                insult = random.choice(insults)  # Triem insult aleatori
                self.client.publish(self.channel_name, insult)  # Publiquem insult
                print(f"Insult enviat: {insult}")
            time.sleep(5)

insult_service = InsultService() #Crear serveo

broadcaster_thread = threading.Thread(target=insult_service.broadcast_insults, daemon=True) # Iniciar broadcaster en thread
broadcaster_thread.start()

insult_service.add_insult("Ets més lent que un caragol amb crosses!")
insult_service.add_insult("Tens menys gràcia que un cactus en un globus!")
insult_service.add_insult("El teu cervell està en mode avió... i sense wifi!")

print("Insults emmagatzemats:", insult_service.get_insults())
