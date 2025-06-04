import pika
import time
from math import ceil
import subprocess
import os
import threading
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import MaxNLocator


class ScalingManager:
    def __init__(self):
        self.active_workers = 0
        self.worker_processes = []

        # RabbitMQ setup
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('localhost', credentials=credentials)
        self.monitor_connection = pika.BlockingConnection(parameters)
        self.monitor_channel = self.monitor_connection.channel()
        self.monitor_channel.queue_declare(queue='insult_queue', durable=True)

        # Parámetros de procesamiento
        self.T = 0.05  # Tiempo por mensaje (ajustado al sleep que añadiste)
        self.C = 20    # Capacidad del worker (msg/s)

        # Datos para cálculos
        self.arrival_rate = 0
        self.lock = threading.Lock()
        self.message_counter = 0
        self.arrival_lock = threading.Lock()

        # Historial en memoria para graficar
        self.timestamps = []
        self.arrival_history = []
        self.worker_history = []

    def get_queue_stats(self):
        try:
            temp_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            temp_channel = temp_connection.channel()
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
        def callback(ch, method, properties, body):
            with self.arrival_lock:
                self.message_counter += 1
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return callback

    def arrival_rate_thread(self, interval=5):
        count_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        count_channel = count_connection.channel()
        count_channel.queue_declare(queue='insult_queue', durable=True)
        count_channel.basic_consume(
            queue='insult_queue',
            on_message_callback=self.count_incoming_messages(),
            auto_ack=False
        )

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
                    lambda_val = delta / time_elapsed if time_elapsed > 0 else 0
                    self.arrival_rate = lambda_val

                stats = self.get_queue_stats()
                print(f"[📊 Métricas] Entrantes: {delta} | "
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
                print(f"🛑 Worker terminado. Activos: {self.active_workers}")
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

    def plot_metrics(self):
        fig, ax1 = plt.subplots(figsize=(10, 5))
        fig.suptitle("📈 Escalado dinámico en tiempo real", fontsize=16)

        # Eje secundario para los workers (a la derecha)
        ax2 = ax1.twinx()

        def animate(i):
            try:
                ax1.clear()
                ax2.clear()

                # Etiquetas y títulos
                ax1.set_xlabel("⏱ Tiempo")
                ax1.set_ylabel("Tasa de llegada λ (msg/s)", color='blue')
                ax2.set_ylabel("Workers activos", color='red')
                ax2.yaxis.set_label_position('right')
                ax2.yaxis.tick_right()

                # Grillas
                ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

                # Gráficos
                ax1.plot(self.timestamps, self.arrival_history, label='λ (msg/s)', color='blue', linewidth=2)
                ax2.plot(self.timestamps, self.worker_history, label='Workers', color='red', linewidth=2)

                # Ejes de color coordinado
                ax1.tick_params(axis='y', labelcolor='blue')
                ax2.tick_params(axis='y', labelcolor='red')
                ax2.yaxis.set_major_locator(MaxNLocator(integer=True))


                # Rotar etiquetas del eje X
                plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

                # Leyendas
                ax1.legend(loc='upper left')
                ax2.legend(loc='upper right')

                plt.tight_layout()
            except Exception as e:
                print(f"⚠️ Error actualizando gráfico: {e}")

        ani = animation.FuncAnimation(fig, animate, interval=5000)
        plt.show()



    def run(self):
        threading.Thread(target=self.arrival_rate_thread, daemon=True).start()
        threading.Thread(target=self.plot_metrics, daemon=True).start()

        try:
            print("🚀 Monitor de escalamiento dinámico iniciado")
            if self.active_workers == 0:
                self.start_worker()

            while True:
                with self.lock:
                    lambda_val = self.arrival_rate

                required_workers = self.calculate_required_workers(lambda_val)
                self.scale_workers(required_workers)

                timestamp = datetime.now().strftime('%H:%M:%S')
                self.timestamps.append(timestamp)
                self.arrival_history.append(lambda_val)
                self.worker_history.append(self.active_workers)

                # Limitar a los últimos 60 puntos para mantener el gráfico limpio
                if len(self.timestamps) > 60:
                    self.timestamps.pop(0)
                    self.arrival_history.pop(0)
                    self.worker_history.pop(0)

                print(f"[LOG] {timestamp} | λ={lambda_val:.2f} | Workers={self.active_workers} | Requeridos={required_workers}")
                time.sleep(2)
        except KeyboardInterrupt:
            print("🛑 Deteniendo monitor...")
            self.monitor_connection.close()

if __name__ == "__main__":
    manager = ScalingManager()
    manager.run()
