import pika
import time
import random

insults = [
    "Eres más lento que una tortuga con resaca.",
    "Tienes la gracia de un error 404.",
    "Tu código tiene más bugs que una colmena.",
    "Tu lógica es tan sólida como una gelatina.",
    "Ni el compilador te entiende."
]

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='insult_queue', durable=True)

for i in range(100):  # Enviamos 100 insultos rápidamente
    insult = random.choice(insults)
    channel.basic_publish(
        exchange='',
        routing_key='insult_queue',
        body=insult,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistente
            correlation_id=str(i)
        )
    )
    print(f"[Client] Enviado insulto #{i + 1}: {insult}")
    time.sleep(0.1)  # MUY rápido (10 mensajes por segundo aprox.)

connection.close()
