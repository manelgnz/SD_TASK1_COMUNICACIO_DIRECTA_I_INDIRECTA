import pika
import time
from math import ceil
import subprocess
import os
import threading
import csv
from datetime import datetime

class ScalingManager:
    def __init__(self):
        self.active_workers = 0
        self.worker_processes = []

        self.csv_file = 'scaling_metrics.csv'
        self._init_csv()

        # RabbitMQ setup
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('localhost', credentials=credentials)
        self.monitor_connection = pika.BlockingConnection(parameters)
        self.monitor_channel = self.monitor_connection.channel()
        self.monitor_channel.queue_declare(queue='insult_queue', durable=True)

        # Parámetros de procesamiento
        self.T =  1.0004  # Tiempo de procesamiento por mensaje (segundos)
        self.C = 2500    # Capacidad del worker (msg/seg)

        # Para tasa de llegada
        self.arrival_rate = 0
        self.lock = threading.Lock()
     
        # ... (código existente)
        self.message_counter = 0
        self.arrival_lock = threading.Lock()

    def _init_csv(self):
        with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Arrival Rate', 'Active Workers', 'Required Workers'])

    def _write_to_csv(self, lambda_val, active_workers, required_workers):
        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                f"{lambda_val:.2f}",
                active_workers,
                required_workers
            ])

    def get_queue_stats(self):
        try:
            temp_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            temp_channel = temp_connection.channel()
            
            # Obtener estadísticas de la cola
            queue = temp_channel.queue_declare(queue='insult_queue', passive=True)
            stats = {
                'messages': queue.method.message_count,
                'consumers': queue.method.consumer_count
            }
            
            temp_connection.close()
            return stats
        except Exception as e:
            print(f"⚠️ Error obteniendo estadísticas: {e}")
            return {'messages': 0, 'consumers': 0}

    def count_incoming_messages(self):
        """Callback que cuenta los mensajes entrantes"""
        def callback(ch, method, properties, body):
            with self.arrival_lock:
                self.message_counter += 1
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        return callback

    def arrival_rate_thread(self, interval=5):
        # Configurar un consumer solo para contar mensajes
        count_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        count_channel = count_connection.channel()
        count_channel.queue_declare(queue='insult_queue', durable=True)
        count_channel.basic_consume(queue='insult_queue',
                                on_message_callback=self.count_incoming_messages(),
                                auto_ack=False)
        
        # Iniciar hilo para el consumer contador
        counting_thread = threading.Thread(target=lambda: count_channel.start_consuming())
        counting_thread.daemon = True
        counting_thread.start()

        while True:
            try:
                start_time = time.time()
                initial_count = self.message_counter
                
                time.sleep(interval)
                
                end_time = time.time()
                with self.arrival_lock:
                    final_count = self.message_counter
                    delta = final_count - initial_count
                    time_elapsed = end_time - start_time
                    lambda_val = delta / time_elapsed
                    self.arrival_rate = lambda_val

                stats = self.get_queue_stats()
                print(f"[📊 Métricas] Mensajes entrantes: {delta} | "
                    f"Tasa: {lambda_val:.2f} msg/s | "
                    f"En cola: {stats['messages']} | "
                    f"Consumidores: {stats['consumers']}")
                
            except Exception as e:
                print(f"Error en hilo de medición: {e}")
                time.sleep(1)
    def start_worker(self):
        worker_script = os.path.join(os.path.dirname(__file__), 'insult_service.py')
        try:
            process = subprocess.Popen(['python', worker_script])
            self.worker_processes.append(process)
            self.active_workers += 1
            print(f"✅ Worker {self.active_workers} iniciado")
            return True
        except Exception as e:
            print(f"❌ Error al iniciar worker: {str(e)}")
            return False

    def terminate_worker(self):
        if self.worker_processes:
            process = self.worker_processes.pop()
            try:
                process.terminate()
                process.wait(timeout=2)
                self.active_workers -= 1
                print(f"🛑 Worker terminado. Workers activos: {self.active_workers}")
            except Exception as e:
                print(f"⚠️ Error al terminar worker: {e}")

    def scale_workers(self, required_workers):
        delta = required_workers - self.active_workers

        if delta > 0:
            print(f"📈 Escalando: +{delta} workers")
            for _ in range(delta):
                if not self.start_worker():
                    break
        elif delta < 0:
            print(f"📉 Reducción: -{-delta} workers")
            for _ in range(-delta):
                self.terminate_worker()

    def calculate_required_workers(self, lambda_val):
        return max(1, ceil((lambda_val * self.T) / self.C))

    def run(self):
        threading.Thread(target=self.arrival_rate_thread, daemon=True).start()

        try:
            print("🚀 Monitor de escalamiento dinámico iniciado")
            if self.active_workers == 0:
                self.start_worker()

            while True:
                with self.lock:
                    lambda_val = self.arrival_rate

                required_workers = self.calculate_required_workers(lambda_val)
                self.scale_workers(required_workers)

                log_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {lambda_val:.2f}, {self.active_workers}, {required_workers}"
                print(log_msg)
                self._write_to_csv(lambda_val, self.active_workers, required_workers)

                time.sleep(5)
        except KeyboardInterrupt:
            print("🛑 Deteniendo monitor...")
            self.monitor_connection.close()

if __name__ == "__main__":
    manager = ScalingManager()
    manager.run()
