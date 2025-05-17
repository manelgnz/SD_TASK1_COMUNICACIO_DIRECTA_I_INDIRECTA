import pika

NUM_INSULTOS = 50000  # Número de insultos a enviar

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Cola principal de insultos
channel.queue_declare(queue='insult_queue', durable=True)

# Publicamos los insultos
for i in range(NUM_INSULTOS):
    insulto = f"Insulto #{i+1}..."
    channel.basic_publish(
        exchange='',
        routing_key='insult_queue',
        body=insulto.encode(),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    print(f"[Cliente] Insulto enviado: {insulto}")

# Enviamos el mensaje de finalización
channel.basic_publish(
    exchange='',
    routing_key='insult_queue',
    body=b"FIN",
    properties=pika.BasicProperties(delivery_mode=2),
)
print("[Cliente] Mensaje de FIN enviado.")

# Cerramos la conexión
connection.close()
