import pika
import random
import time

# Lista donde almacenamos los insultos
insults = []

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Cola donde recibimos insultos
channel.queue_declare(queue='insult_queue', durable=True)

# Cola donde publicaremos los insultos aleatorios
channel.queue_declare(queue='insult_broadcast', durable=True)

# Cola para enviar notificaciones de finalización al cliente
channel.queue_declare(queue='done_queue', durable=True)

# Función para publicar un insulto aleatorio cada 5 segundos
def insult_broadcaster():
    broadcaster_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    broadcaster_channel = broadcaster_connection.channel()
    broadcaster_channel.queue_declare(queue='insult_broadcast', durable=True)

    while True:
        if insults:
            random_insult = random.choice(insults)
            broadcaster_channel.basic_publish(
                exchange='',
                routing_key='insult_broadcast',
                body=random_insult,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            print(f"[Broadcast] Insulto enviado: {random_insult}")
        time.sleep(5)

# Hilo para el broadcaster de insultos
import threading
broadcaster_thread = threading.Thread(target=insult_broadcaster)
broadcaster_thread.daemon = True
broadcaster_thread.start()

# Callback que maneja los insultos que llegan a la cola
def callback(ch, method, properties, body):
    insult = body.decode()
    
    if insult not in insults:
        insults.append(insult)
        print(f"[Worker] Insulto agregado: {insult}")
    else:
        print(f"[Worker] El insulto ya existe: {insult}")

    # Confirmamos que procesamos el mensaje
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Enviamos una notificación al cliente sobre el procesamiento
    response = f"Insulto '{insult}' procesado"
    ch.basic_publish(
        exchange='',
        routing_key='done_queue',  # Cola donde el cliente espera la confirmación
        body=response,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id  # Identificador de correlación
        )
    )

# Consumir los insultos que llegan a la cola
channel.basic_consume(queue='insult_queue', on_message_callback=callback)

print('[*] Esperando insultos...')
channel.start_consuming()
