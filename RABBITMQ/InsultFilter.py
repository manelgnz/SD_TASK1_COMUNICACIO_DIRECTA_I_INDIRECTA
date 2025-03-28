#!/usr/bin/env python
import pika
import threading

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare queues
channel.queue_declare(queue='insult_broadcast', durable=True)  # Queue to subscribe to InsultService
channel.queue_declare(queue='client_messages', durable=True)  # Queue to receive messages from clients

print(' [*] InsultFilter is running. To exit press CTRL+C')

stored_messages = []  # List to store all messages
insults = ["insult1", "insult2", "insult3"]  # Replace with actual insults

def handle_broadcast(ch, method, properties, body):
    """Handle messages from the insult_broadcast queue."""
    message = body.decode()
    if message in insults:
        censored_message = "CENSORED"
        stored_messages.append(censored_message)
        print(f" [x] Received insult and censored: {message}")
    else:
        stored_messages.append(message)
        print(f" [x] Received and stored: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def handle_client_messages(ch, method, properties, body):
    """Handle messages from the client_messages queue."""
    message = body.decode()
    if message in insults:
        censored_message = "CENSORED"
        stored_messages.append(censored_message)
        print(f" [x] Received client insult and censored: {message}")
    else:
        stored_messages.append(message)
        print(f" [x] Received client message and stored: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_broadcast_listener():
    """Start listening to the insult_broadcast queue."""
    channel.basic_consume(queue='insult_broadcast', on_message_callback=handle_broadcast)
    channel.start_consuming()

def start_client_listener():
    """Start listening to the client_messages queue."""
    channel.basic_consume(queue='client_messages', on_message_callback=handle_client_messages)
    channel.start_consuming()

# Start listeners in separate threads
broadcast_thread = threading.Thread(target=start_broadcast_listener, daemon=True)
client_thread = threading.Thread(target=start_client_listener, daemon=True)

broadcast_thread.start()
client_thread.start()

# Keep the main thread alive
try:
    while True:
        pass
except KeyboardInterrupt:
    print(" [*] Exiting...")
    connection.close()