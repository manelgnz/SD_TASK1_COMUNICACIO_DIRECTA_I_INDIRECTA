import pika
import random
import time

INSULTS = {
    "idiota", "tonto", "imbècil", "burro", "cap de suro",
    "mal educat", "bàrbar", "malparit", "ruc", "dropo"
}
NUM_MENSAJES = 100000

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='filtro_insultos', durable=True)


# Creamos un canal exclusivo para recibir la confirmación final
done_channel = connection.channel()



start_time = time.time()

for i in range(NUM_MENSAJES):
    if i % 2 == 0:
        mensaje = f"Mensaje limpio #{i+1}"
    else:
        mensaje = random.choice(list(INSULTS))

    channel.basic_publish(
        exchange='',
        routing_key='filtro_insultos',
        body=mensaje.encode(),
        properties=pika.BasicProperties(delivery_mode=2),
    )

# Enviar mensaje final
channel.basic_publish(
    exchange='',
    routing_key='filtro_insultos',
    body="FIN".encode(),
    properties=pika.BasicProperties(delivery_mode=2),
)
print(f"[Cliente] Enviados {NUM_MENSAJES} mensajes + FIN")



connection.close()
