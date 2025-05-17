import pika
import time

INSULTS = {
    "idiota", "tonto", "imbècil", "burro", "cap de suro",
    "mal educat", "bàrbar", "malparit", "ruc", "dropo"
}

start_time = None
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='filtro_insultos', durable=True)
channel.queue_declare(queue='done_queue', durable=True)

def callback(ch, method, properties, body):
    global start_time

    mensaje = body.decode()

    if mensaje == "FIN":
        end_time = time.time()
        total = end_time - start_time
        print(f"\n✅ Todos los mensajes procesados.")
        print(f"⏱️ Tiempo total (worker interno): {total:.4f} segundos")

        # Enviar confirmación final al cliente
        ch.basic_publish(
            exchange='',
            routing_key='done_queue',
            body="DONE"
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()
        return

    if start_time is None:
        start_time = time.time()

    if mensaje in INSULTS:
        print(f"[FILTRADO] Insulto detectado: {mensaje}")
    else:
        print(f"[OK] Mensaje limpio: {mensaje}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='filtro_insultos', on_message_callback=callback)
print('[*] Esperando mensajes...')
channel.start_consuming()

channel.close()
connection.close()
