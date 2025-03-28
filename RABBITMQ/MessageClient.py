#!/usr/bin/env python
import pika

if __name__ == "__main__":
    # Hardcoded list of messages
    messages = [
        "hola que tal",
        "buenas tardes",
        "buenos dias",
        "hasta luego",
        "messi la cabra"
    ]

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare the queue to ensure it exists
    channel.queue_declare(queue='client_messages', durable=True)

    for message in messages:
        # Publish the message to the client_messages queue ( insultFilter)
        channel.basic_publish(
            exchange='',
            routing_key='client_messages',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        print(f" [x] Sent: {message}")

    connection.close()
    print("All messages sent!")