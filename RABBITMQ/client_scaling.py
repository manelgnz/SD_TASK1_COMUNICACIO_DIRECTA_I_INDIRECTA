import pika
import time
import uuid
import csv
import os
from datetime import datetime

NUM_INSULTOS = 100000

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='insult_queue', durable=True)
channel.queue_declare(queue='done_queue', durable=True)

# Tiempos para métricas
start_send_time = time.time()

# Publicamos insultos
for i in range(NUM_INSULTOS):
    insulto = f"Insulto #{i+1}..."
    channel.basic_publish(
        exchange='',
        routing_key='insult_queue',
        body=insulto,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ),
    )
    if (i + 1) % 1000 == 0:
        print(f"[Cliente] {i + 1} insultos enviados...")

end_send_time = time.time()
send_duration = end_send_time - start_send_time
lambda_rate = NUM_INSULTOS / send_duration  # λ

received = 0
start_process_time = time.time()

def callback(ch, method, properties, body):
    global received, start_process_time
    received += 1

    if received == NUM_INSULTOS:
        total_processing_time = time.time() - start_process_time
        avg_T = total_processing_time / NUM_INSULTOS  # T
        C = 1 / avg_T  # Capacidad de 1 worker

        print(f"\n[✓] Todos los insultos han sido procesados.")
        print(f"[Métrica] λ (tasa llegada) = {lambda_rate:.2f} msg/s")
        print(f"[Métrica] T (tiempo promedio procesamiento) = {avg_T:.4f} s/msg")
        print(f"[Métrica] C (capacidad de un worker) = {C:.2f} msg/s\n")

        # Guardar resultados
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = "resultados.csv"
        write_header = not os.path.exists(file_path)

        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    "Timestamp",
                    "Num_Insultos",
                    "Duracion_Envio (s)",
                    "Lambda (msg/s)",
                    "Duracion_Procesamiento (s)",
                    "T (s/msg)",
                    "C (msg/s)"
                ])
            writer.writerow([
                timestamp,
                NUM_INSULTOS,
                round(send_duration, 4),
                round(lambda_rate, 2),
                round(total_processing_time, 4),
                round(avg_T, 6),
                round(C, 2)
            ])
        
        ch.stop_consuming()

channel.basic_consume(queue='done_queue', on_message_callback=callback, auto_ack=True)

print("[Cliente] Esperando confirmaciones de los workers...")
channel.start_consuming()

connection.close()
