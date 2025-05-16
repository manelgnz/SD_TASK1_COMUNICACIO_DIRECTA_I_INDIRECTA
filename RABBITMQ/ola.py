import pika
import threading
import time
import random
from datetime import datetime

class StressTester:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='insult_queue', durable=True)
        
        # Estadísticas
        self.sent_count = 0
        self.received_count = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        # Configuración
        self.max_workers = 5  # Número máximo de hilos de envío
        self.test_duration = 30  # Duración de la prueba en segundos
        self.message_rate = 50000  # Mensajes por segundo (por worker)

    def send_messages(self, worker_id):
        """Hilo que envía mensajes constantemente"""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            
            while time.time() - self.start_time < self.test_duration:
                insult = f"Insulto #{random.randint(1, 1000)} from worker {worker_id}"
                channel.basic_publish(
                    exchange='',
                    routing_key='insult_queue',
                    body=insult,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Persistente
                    )
                )
                
                with self.lock:
                    self.sent_count += 1
                
                # Control de tasa de envío
                time.sleep(0.5 / self.message_rate)
                
            connection.close()
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")

    def monitor_results(self):
        """Consume las respuestas para medir el rendimiento"""
        def callback(ch, method, properties, body):
            with self.lock:
                self.received_count += 1
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='done_queue', durable=True)
        channel.basic_consume(queue='done_queue', on_message_callback=callback)
        
        print("Iniciando monitor de resultados...")
        channel.start_consuming()

    def run_test(self):
        # Iniciar hilos de envío
        send_threads = []
        for i in range(self.max_workers):
            t = threading.Thread(target=self.send_messages, args=(i,))
            t.daemon = True
            t.start()
            send_threads.append(t)
        
        # Iniciar monitor de resultados
        monitor_thread = threading.Thread(target=self.monitor_results)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Mostrar estadísticas periódicamente
        try:
            while time.time() - self.start_time < self.test_duration:
                time.sleep(5)
                elapsed = time.time() - self.start_time
                with self.lock:
                    sent = self.sent_count
                    received = self.received_count
                    backlog = sent - received
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Enviados: {sent} | "
                      f"Recibidos: {received} | "
                      f"Backlog: {backlog} | "
                      f"Tasa: {received/elapsed:.2f} msg/s")
        
        except KeyboardInterrupt:
            print("\nDeteniendo prueba...")
        
        # Resultados finales
        elapsed = time.time() - self.start_time
        print("\n=== RESULTADOS FINALES ===")
        print(f"Duración: {elapsed:.2f} segundos")
        print(f"Total enviados: {self.sent_count}")
        print(f"Total recibidos: {self.received_count}")
        print(f"Tasa promedio: {self.received_count/elapsed:.2f} mensajes/segundo")
        print(f"Porcentaje procesado: {100*self.received_count/max(1, self.sent_count):.2f}%")
        
        self.connection.close()

if __name__ == "__main__":
    tester = StressTester()
    print("=== INICIANDO PRUEBA DE ESTRÉS ===")
    print(f"Configuración: {tester.max_workers} workers, {tester.message_rate} msg/s por worker")
    print(f"Duración: {tester.test_duration} segundos")
    tester.run_test()