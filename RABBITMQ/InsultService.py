#!/usr/bin/env python
import pika
import time
import threading

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare durable queue to avoid losing messages if the worker crashes
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='insult_broadcast', durable=True)  # Queue for broadcasting insults

print(' [*] Waiting for messages. To exit press CTRL+C')

received_messages = []  # List to store new insults

def callback(ch, method, properties, body):
    message = body.decode()
    if message not in received_messages:
        received_messages.append(message)
        print(f" [x] Received and stored: {message}")
    else:
        print(f" [x] Duplicate message ignored: {message}")
    
    time.sleep(5)
    print(" [x] Done")
    # Acknowledge the message and remove it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)

def insult_broadcaster():
    while True:
        if received_messages:  # Only broadcast if there are insults in the list
            for insult in received_messages:
                channel.basic_publish(
                    exchange='',
                    routing_key='insult_broadcast',
                    body=insult
                )
                print(f" [x] Broadcasted insult: {insult}")
                time.sleep(5)  # Wait 5 seconds before broadcasting the next insult
        else:
            print(" [x] No insults to broadcast. Waiting...")
            time.sleep(5)

# Set up the consumer for receiving insults
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

# Start the insult broadcaster in a separate thread
broadcaster_thread = threading.Thread(target=insult_broadcaster, daemon=True)
broadcaster_thread.start()

# Start consuming messages
channel.start_consuming()