import pika
import random
import time
import threading

# Lista donde almacenamos los insultos
insults = []

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declaración de colas
channel.queue_declare(queue='insult_queue', durable=True)
channel.queue_declare(queue='insult_broadcast', durable=True)
channel.queue_declare(queue='done_queue', durable=True)

# Variables para medir el tiempo
start_time = None
total_insults = 0

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
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"[Broadcast] Insulto enviado: {random_insult}")
        time.sleep(5)

# Lanzar hilo para emitir insultos
broadcaster_thread = threading.Thread(target=insult_broadcaster)
broadcaster_thread.daemon = True
broadcaster_thread.start()

# Callback principal
def callback(ch, method, properties, body):
    global start_time, total_insults
    insult = body.decode()

    # Iniciar cronómetro al recibir el primer mensaje
    if start_time is None and insult != "FIN":
        start_time = time.time()

    if insult == "FIN":
        print("\n✅ Fin de procesamiento recibido.")
        end_time = time.time()

        total_time = end_time - start_time if start_time else 0
        print(f"📋 Total de insultos procesados: {total_insults}")
        print(f"⏱️ Tiempo total: {total_time:.2f} segundos")

        if total_time > 0:
            print(f"📈 Capacidad promedio: {total_insults / total_time:.2f} mensajes/segundo")
            print(f"🧮 Tiempo promedio por mensaje: {total_time / total_insults:.4f} segundos")

        # Enviar confirmación al cliente
        ch.basic_publish(
            exchange='',
            routing_key='done_queue',
            body="DONE"
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if insult not in insults:
        insults.append(insult)
        print(f"[Worker] Insulto agregado: {insult}")
    else:
        print(f"[Worker] El insulto ya existe: {insult}")

    total_insults += 1
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Iniciar consumo
channel.basic_consume(queue='insult_queue', on_message_callback=callback)
print('[*] Esperando insultos...')
channel.start_consuming()
