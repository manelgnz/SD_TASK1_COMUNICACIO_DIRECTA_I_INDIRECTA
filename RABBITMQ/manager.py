import pika
import random
import time
import multiprocessing
from multiprocessing import Process, Queue
import math

# Worker Function (multiprocessing)
def worker_function(queue, done_queue):
    while True:
        insult = queue.get()
        if insult == 'STOP':  # Stop signal
            break
        # Process insult
        time.sleep(random.uniform(0.1, 0.5))  # Simulating processing time
        response = f"Processed {insult}"
        done_queue.put(response)
        print(f"[Worker] {response}")

# Function to dynamically scale the workers
def dynamic_scaling(message_arrival_rate, processing_time, worker_capacity):
    # Calculate required number of workers
    required_workers = math.ceil((message_arrival_rate * processing_time) / worker_capacity)
    return required_workers

# Start workers and adjust dynamically
def start_dynamic_workers():
    message_arrival_rate = 100  # Example rate of messages per second
    processing_time = 0.2  # Example processing time per message in seconds
    worker_capacity = 1000  # Example worker capacity in messages per second

    # Create the main queue for task distribution and done queue for responses
    task_queue = Queue()
    done_queue = Queue()

    # Calculate the number of workers needed
    required_workers = dynamic_scaling(message_arrival_rate, processing_time, worker_capacity)
    workers = []

    # Start worker processes
    for _ in range(required_workers):
        p = Process(target=worker_function, args=(task_queue, done_queue))
        p.start()
        workers.append(p)

    # Add messages to the queue
    for i in range(1000):  # Example number of insults
        task_queue.put(f"Insulto #{i + 1}")
    
    # Collect the results
    for _ in range(1000):
        print(done_queue.get())

    # Stop workers
    for _ in range(required_workers):
        task_queue.put('STOP')
    
    for p in workers:
        p.join()

# Run the dynamic scaling mechanism
if __name__ == "__main__":
    start_dynamic_workers()
