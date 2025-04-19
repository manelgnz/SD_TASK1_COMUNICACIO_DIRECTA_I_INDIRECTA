import redis
import time
import threading

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
QUEUE = "text_queue"
RESULT_KEY = "filtered_results"
INSULTS_KEY = "insult_list"

# === Filter Logic ===

def send_text_for_filtering(text: str):
    redis_client.rpush(QUEUE, text)
    #print(f"[Sent for filtering] {text}")

def filter_worker():
    while True:
        msg = redis_client.blpop(QUEUE, timeout=5)
        if msg:
            _, text = msg
            insults = list(redis_client.smembers(INSULTS_KEY))
            for insult in insults:
                text = text.replace(insult, "CENSORED")
            redis_client.rpush(RESULT_KEY, text)
            #print(f"[Filtered] {text}")

def get_filtered_results():
    return redis_client.lrange(RESULT_KEY, 0, -1)

# === Demo / Test ===

if __name__ == "__main__":
    # Start worker in background thread
    print("Starting filter worker...")
    threading.Thread(target=filter_worker, daemon=True).start()

    # Send test messages
    time.sleep(1)  # Ensure worker starts first
    send_text_for_filtering("Hey Noob, how are you?")
    send_text_for_filtering("You're a fool! This is bad.")

    # Wait and fetch results
    time.sleep(3)
    print("Filtered results:")
    print(get_filtered_results())

    # Keep main thread alive to allow continuous filtering
    while True:
        time.sleep(1)
