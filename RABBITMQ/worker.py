import pika
import time
import os

worker_id = os.getenv("WORKER_ID", "worker")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='done_queue', durable=True)

print(f'[{worker_id}] Esperando tareas...')

def callback(ch, method, properties, body):
    task = body.decode()
    print(f"[{worker_id}] Procesando: {task}")

    start_time = time.time()
    time.sleep(task.count('.') * 0.5)  # Simula tarea
    end_time = time.time()

    duration = end_time - start_time
    print(f"[{worker_id}] Hecho: {task} en {duration:.2f} segundos")

    # Publicar en done_queue con el tiempo que tomó
    channel.basic_publish(
        exchange='',
        routing_key='done_queue',
        body=f"{task} completada por {worker_id} en {duration:.2f} s"
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()
