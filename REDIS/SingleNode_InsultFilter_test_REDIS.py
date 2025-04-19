import time
import random
import threading
from InsultFilter_REDIS import send_text_for_filtering, filter_worker
import redis

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
QUEUE = "text_queue"
RESULT_KEY = "filtered_results"

def benchmark_insult_filter_single_node(n_requests=3000):
    print(f"\n[Benchmark] InsultFilter (Single Node) - Processing {n_requests} messages")

    # Clear previous test data
    redis_client.delete(QUEUE)
    redis_client.delete(RESULT_KEY)

    # Asegurar que los insultos estén definidos en un SET
    redis_client.delete("insult_list")
    redis_client.sadd("insult_list", "Noob!", "You're a fool!", "Clown!")

    # Prepare insult messages
    insults = ["Noob!", "You're a fool!", "Clown!"]
    messages = [f"This guy is a {random.choice(insults)}" for _ in range(n_requests)]

    # Start the filter worker in a separate thread
    worker_thread = threading.Thread(target=filter_worker, args=(), daemon=True)
    worker_thread.start()

    # Start timing
    start = time.time()

    for msg in messages:
        send_text_for_filtering(msg)

    # Wait until all messages are filtered
    while redis_client.llen(RESULT_KEY) < n_requests:
        time.sleep(0.1)

    elapsed = time.time() - start
    print(f"Processed {n_requests} messages in {elapsed:.2f} seconds")
    print(f"Throughput: {n_requests / elapsed:.2f} messages/sec")

    # Sanity check: Count filtered results
    count = redis_client.llen(RESULT_KEY)
    print(f"Stored {count} filtered messages")

if __name__ == "__main__":
    benchmark_insult_filter_single_node()
