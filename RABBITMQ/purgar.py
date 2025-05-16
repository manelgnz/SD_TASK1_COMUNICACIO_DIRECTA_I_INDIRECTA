import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Cola donde recibimos insultos
channel.queue_purge(queue='insult_queue')
print("[✓] Cola 'insult_queue' purgada.")
connection.close()