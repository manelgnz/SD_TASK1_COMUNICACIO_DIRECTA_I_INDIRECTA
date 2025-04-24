import threading
from xmlrpc.server import SimpleXMLRPCServer
import time
import redis  # Import Redis library
import argparse  # Para manejar argumentos de línea de comandos

class InsultFilter:
    def __init__(self):
        # Connect to Redis
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        self.result_list = []  # List to store filtered texts
        self.work_queue = []  # Queue to store texts to be processed
        print("[InsultFilter] Initialized with an empty result list and work queue.")

    def set_insults(self, insults):
        """
        Set the list of insults in Redis.
        :param insults: List of insults to be stored in Redis.
        """
        print(f"[InsultFilter] Setting insults: {insults}")
        for insult in insults:
            self.redis_client.sadd("insults", insult)
        return True

    def filter_text(self, text):
        """
        Filter a given text by replacing insults with 'CENSORED'.
        :param text: The text to be filtered.
        :return: The filtered text.
        """
        print(f"[InsultFilter] Filtering text: '{text}'")
        insults = list(self.redis_client.smembers("insults"))  # Get insults from Redis
        for insult in insults:
            if insult in text:
                print(f"[InsultFilter] Found insult '{insult}' in text. Replacing with 'CENSORED'.")
            text = text.replace(insult, "CENSORED")
        self.result_list.append(text)  # Add the filtered text to the result list
        print(f"[InsultFilter] Filtered text: '{text}' added to result list.")
        return text

    def get_filtered_results(self):
        """
        Retrieve the list of all filtered texts.
        :return: List of filtered texts.
        """
        print(f"[InsultFilter] Returning filtered results: {self.result_list}")
        return self.result_list

    def add_to_work_queue(self, text):
        """
        Add a text to the work queue for processing.
        :param text: The text to be added to the queue.
        """
        print(f"[InsultFilter] Adding text to work queue: '{text}'")
        self.work_queue.append(text)

    def process_queue(self):
        """
        Continuously process texts from the work queue.
        If the queue is empty, wait for new tasks.
        """
        print("[InsultFilter] Processing work queue...")
        while True:
            if self.work_queue:
                text = self.work_queue.pop(0)  # Get the first text from the queue
                print(f"[InsultFilter] Processing text from queue: '{text}'")
                self.filter_text(text)  # Filter the text
            else:
                print("[InsultFilter] Work queue is empty. Waiting for new tasks...")
            time.sleep(2)  # Wait for 2 seconds before checking the queue again

if __name__ == "__main__":
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Start an InsultFilter node.")
    parser.add_argument("--port", type=int, default=9000, help="Port number for the InsultFilter")
    args = parser.parse_args()

    # Usar el puerto especificado
    server = SimpleXMLRPCServer(("localhost", args.port), allow_none=True)
    service = InsultFilter()

    # Register the methods of InsultFilter as XML-RPC functions
    server.register_function(service.filter_text, "filter_text")
    server.register_function(service.get_filtered_results, "get_filtered_results")
    server.register_function(service.set_insults, "set_insults")

    # Start processing the work queue in a separate thread
    threading.Thread(target=service.process_queue, daemon=True).start()

    try:
        print(f"[InsultFilter] InsultFilter is running on port {args.port}...")
        server.serve_forever()  # Start the XML-RPC server
    except KeyboardInterrupt:
        print("[InsultFilter] Shutting down InsultFilter...")
        server.server_close()  # Close the server gracefully