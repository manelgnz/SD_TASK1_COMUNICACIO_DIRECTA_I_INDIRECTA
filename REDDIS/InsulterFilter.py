import redis

class InsultFilter:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.queue_name = "task_queue"
        self.result_list = "resultsList"
        self.insult_list_name = "insultList"  # Nom de la llista d'insults a Redis

    def process_messages(self):  # Processa els missatges de la cua i els filtra
        print("El consumidor està esperant tasques...")
        while True:
            task = self.client.blpop(self.queue_name, timeout=10)  # Timeout (evitar bloquejos infinits)
            if task:
                msg = task[1]  # task[0] és el nom de la cua, task[1] és el missatge
                insults = self.client.lrange(self.insult_list_name, 0, -1)  # Obtenim la llista d'insults de Redis
                if msg in insults:  # Si el missatge és un insult, el censurarem
                    print(f"Insult detectat: {msg}")
                    self.client.rpush(self.result_list, "CENSORED")
                else:
                    print(f"Missatge afegit: {msg}")
                    self.client.rpush(self.result_list, msg)

    def add_insult(self, insult):  # Afegeix un insult a la llista si no hi és ja.
        insults = self.client.lrange(self.insult_list_name, 0, -1)  # Obtenim la llista d'insults
        if insult not in insults:
            self.client.rpush(self.insult_list_name, insult)  # Afegim l'insult a Redis.
            print(f"Insult afegit: {insult}")

    def get_filtered_results(self):
        return self.client.lrange(self.result_list, 0, -1)


if __name__ == "__main__":
    filter_service = InsultFilter()
    
    filter_service.add_insult("idiota")
    filter_service.add_insult("imbècil")

    filter_service.process_messages()
    