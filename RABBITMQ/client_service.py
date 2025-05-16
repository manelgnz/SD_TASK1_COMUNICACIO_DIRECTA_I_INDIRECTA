import pika
import time
import uuid
import csv
from datetime import datetime

NUM_INSULTOS = 30000  # Número de insultos a enviar

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Cola principal de insultos
channel.queue_declare(queue='insult_queue', durable=True)

# Cola para recibir notificaciones de finalización
channel.queue_declare(queue='done_queue', durable=True)

# Almacenaremos el tiempo total
start_time = time.time()

# Publicamos los insultos
for i in range(NUM_INSULTOS):
    
    insulto = f"Insulto #{i+1}..."
    channel.basic_publish(
        exchange='',
        routing_key='insult_queue',
        body=insulto,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Asegura que el mensaje sea persistente
        ),
    )
    print(f"[Cliente] Insulto enviado: {insulto}")

# Variable para saber cuántos insultos han sido procesados
received = 0

# Callback que maneja las confirmaciones de los workers
def callback(ch, method, properties, body):
    global received
    received += 1

    if received == NUM_INSULTOS:
        # Si todos los insultos fueron procesados, calculamos el tiempo total
        total_time = time.time() - start_time
        average_capacity = NUM_INSULTOS / total_time
        average_msgprocessing = total_time / NUM_INSULTOS  # Tiempo promedio de procesamiento por mensaje

        print(f"[✓] Todos los insultos han sido procesados en {total_time:.2f} segundos.")
        print(f"[📈] Capacidad promedio de procesamiento: {average_capacity:.2f} mensajes/segundo")
        print(f"[⏱️] Tiempo promedio de procesamiento por mensaje: {average_msgprocessing:.4f} segundos")


        # Guardamos los resultados en un archivo CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("resultados.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, NUM_INSULTOS, total_time])
        
        ch.stop_consuming()  # Detenemos la espera de mensajes

# Consumimos los mensajes de la cola 'done_queue' que los workers publican al finalizar
channel.basic_consume(queue='done_queue', on_message_callback=callback, auto_ack=True)

# Comenzamos a consumir mensajes (esperando confirmaciones de finalización)
print("[Cliente] Esperando la confirmación de los workers...")
channel.start_consuming()

# Cerramos la conexión al final (esto se alcanzará cuando se haya procesado todos los insultos)
connection.close()
