import pika
import time
import uuid
import csv
from datetime import datetime


NUM_TAREAS = 20

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Cola principal de tareas
channel.queue_declare(queue='task_queue', durable=True)

# Cola para recibir notificaciones de finalización
channel.queue_declare(queue='done_queue', durable=True)

start_time = time.time()

for i in range(NUM_TAREAS):
    message = f"Tarea #{i+1}..."
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )

# Consumidor temporal para saber cuándo terminan
received = 0

def callback(ch, method, properties, body):
    global received
    received += 1

    if received == NUM_TAREAS:
        total_time = time.time() - start_time
        print(f"[✓] Todas las tareas completadas en {total_time:.2f} segundos")

        # Guardar resultado en CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("resultados.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, NUM_TAREAS, total_time])
        
        ch.stop_consuming()




channel.basic_consume(queue='done_queue', on_message_callback=callback, auto_ack=True)
channel.start_consuming()

connection.close()
