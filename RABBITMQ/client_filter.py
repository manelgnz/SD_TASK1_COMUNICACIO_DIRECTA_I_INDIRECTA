import pika
import random
import time
import uuid
import csv
from datetime import datetime

# Definimos la lista de insultos y mensajes limpios
INSULTS = {
    "idiota", "tonto", "imbècil", "burro", "cap de suro",
    "mal educat", "bàrbar", "malparit", "ruc", "dropo"
}
NUM_MENSAJES = 30000  # Número de mensajes a enviar

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Cola principal para el filtrado de insultos
channel.queue_declare(queue='filtro_insultos', durable=True)

# Cola para recibir confirmaciones de procesamiento
channel.queue_declare(queue='done_queue', durable=True)

# Almacenamos el tiempo de inicio
start_time = time.time()

# Enviamos los mensajes
for i in range(NUM_MENSAJES):
    if i % 2 == 0:
        mensaje = f"Insulto #{i+1}..."
    else:
        mensaje = random.choice(INSULTS)  # Insulto random

    channel.basic_publish(
        exchange='',
        routing_key='filtro_insultos',
        body=mensaje.encode(),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Asegura que el mensaje sea persistente
        ),
    )
    print(f"[Cliente] Mensaje enviado: {mensaje}")

# Variable para saber cuántos mensajes han sido procesados
received = 0

# Callback que maneja las confirmaciones de los workers
def callback(ch, method, properties, body):
    global received
    received += 1

    if received == NUM_MENSAJES:
        # Si todos los mensajes han sido procesados, calculamos el tiempo total
        total_time = time.time() - start_time
        print(f"[✓] Todos los mensajes han sido procesados en {total_time:.2f} segundos.")

        # Guardamos los resultados en un archivo CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("resultados.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, NUM_MENSAJES, total_time])
        
        ch.stop_consuming()  # Detenemos la espera de mensajes

# Consumimos los mensajes de la cola 'done_queue' que los workers publican al finalizar
channel.basic_consume(queue='done_queue', on_message_callback=callback, auto_ack=True)

# Comenzamos a consumir mensajes (esperando las confirmaciones de finalización)
print("[Cliente] Esperando la confirmación de los workers...")
channel.start_consuming()

# Cerramos la conexión al final (esto se alcanzará cuando se haya procesado todos los mensajes)
connection.close()
