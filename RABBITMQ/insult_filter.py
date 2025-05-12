import pika
import random
import time

INSULTS = {
    "idiota", "tonto", "imbècil", "burro", "cap de suro",
    "mal educat", "bàrbar", "malparit", "ruc", "dropo"
}

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Cola donde recibimos insultos
channel.queue_declare(queue='filtro_insultos', durable=True)

# Cola para enviar notificaciones de finalización al cliente
channel.queue_declare(queue='done_queue', durable=True)

# Callback que maneja los insultos que llegan a la cola
def callback(ch, method, properties, body):
    mensaje = body.decode()
    
    if mensaje in INSULTS:
        print(f"[FILTRADO] Insulto detectado: {mensaje}")
    else:
        print(f"[OK] Mensaje limpio: {mensaje}")

    # Confirmamos que procesamos el mensaje
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Enviamos una notificación al cliente sobre el procesamiento
    response = f"Insulto '{mensaje}' procesado"
    ch.basic_publish(
        exchange='',
        routing_key='done_queue',  # Cola donde el cliente espera la confirmación
        body=response,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id  # Identificador de correlación
        )
    )

# Consumir los insultos que llegan a la cola
channel.basic_consume(queue='filtro_insultos', on_message_callback=callback)

print('[*] Esperando insultos...')
channel.start_consuming()
