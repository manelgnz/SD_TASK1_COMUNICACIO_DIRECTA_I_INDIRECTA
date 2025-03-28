#!/usr/bin/env python
import pika

if __name__ == "__main__":
    # Lista de insultos predefinidos
    insults = [
        "You're as bright as a black hole.",
        "You bring everyone so much joy... when you leave the room.",
        "You're proof that even the worst ideas can be successful.",
        "You have something on your chin... no, the third one down.",
        "Your secrets are safe with me. I never even listen when you tell me them."
    ]

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declarar la cola para asegurarse de que existe
    channel.queue_declare(queue='task_queue', durable=True)

    for insult in insults:
        # Publicar el insulto en la cola task_queue
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=insult,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Hacer el mensaje persistente
            )
        )
        print(f" [x] Sent: {insult}")

    connection.close()
    print("All insults sent!")