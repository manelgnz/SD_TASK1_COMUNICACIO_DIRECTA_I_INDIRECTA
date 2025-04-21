import time
import xmlrpc.client
import threading
from statistics import mean

# Performance metrics
latencies = []
errors = 0

# Stress test for InsultService
def stress_test_add_insult(thread_id, num_requests):
    global latencies, errors
    print(f"[Thread {thread_id}] Starting stress test for add_insult with {num_requests} requests.")
    insults = [f"Insult {i} from thread {thread_id}" for i in range(num_requests)]
    for i, insult in enumerate(insults):
        retries = 3
        while retries > 0:
            try:
                local_server = xmlrpc.client.ServerProxy("http://localhost:8000/")
                start_time = time.time()
                response = local_server.add_insult(insult)
                end_time = time.time()
                latencies.append(end_time - start_time)
                if response:
                    print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Successfully added insult '{insult}' in {end_time - start_time:.5f} seconds.")
                else:
                    print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Insult '{insult}' already exists.")
                    errors += 1
                break
            except Exception as e:
                retries -= 1
                print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Error occurred. Retries left: {retries}. Error: {e}")
                if retries == 0:
                    errors += 1

def stress_test_get_insults(thread_id, num_requests):
    global latencies, errors
    print(f"[Thread {thread_id}] Starting stress test for get_insults with {num_requests} requests.")
    for i in range(num_requests):
        try:
            local_server = xmlrpc.client.ServerProxy("http://localhost:8000/")
            start_time = time.time()
            insults = local_server.get_insults()
            end_time = time.time()
            latencies.append(end_time - start_time)
            print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Retrieved insults in {end_time - start_time:.5f} seconds. Total insults: {len(insults)}.")
        except Exception as e:
            errors += 1
            print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Error occurred. Error: {e}")

# Stress test for InsultFilter
def stress_test_filter_text(thread_id, num_requests):
    global latencies, errors
    print(f"[Thread {thread_id}] Starting stress test for filter_text with {num_requests} requests.")
    texts = [f"This is a test with insult {i} from thread {thread_id}" for i in range(num_requests)]
    for i, text in enumerate(texts):
        retries = 3
        while retries > 0:
            try:
                local_server = xmlrpc.client.ServerProxy("http://localhost:8001/")
                start_time = time.time()
                response = local_server.filter_text(text)
                end_time = time.time()
                latencies.append(end_time - start_time)
                print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Filtered text in {end_time - start_time:.5f} seconds. Result: {response}")
                break
            except Exception as e:
                retries -= 1
                print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Error occurred. Retries left: {retries}. Error: {e}")
                if retries == 0:
                    errors += 1

def stress_test_get_filtered_results(thread_id, num_requests):
    global latencies, errors
    print(f"[Thread {thread_id}] Starting stress test for get_filtered_results with {num_requests} requests.")
    for i in range(num_requests):
        try:
            local_server = xmlrpc.client.ServerProxy("http://localhost:8001/")
            start_time = time.time()
            results = local_server.get_filtered_results()
            end_time = time.time()
            latencies.append(end_time - start_time)
            print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Retrieved filtered results in {end_time - start_time:.5f} seconds. Total results: {len(results)}.")
        except Exception as e:
            errors += 1
            print(f"[Thread {thread_id}] Request {i + 1}/{num_requests}: Error occurred. Error: {e}")

# Run stress tests
def run_stress_test():
    num_threads = 3
    num_requests_per_thread = 5

    # Stress test for InsultService
    print("[Main] Starting stress test for add_insult.")
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=stress_test_add_insult, args=(i, num_requests_per_thread))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("[Main] Finished stress test for add_insult.")
    print("[Main] Starting stress test for get_insults.")

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=stress_test_get_insults, args=(i, num_requests_per_thread))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("[Main] Finished stress test for get_insults.")

    # Stress test for InsultFilter
    print("[Main] Starting stress test for filter_text.")
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=stress_test_filter_text, args=(i, num_requests_per_thread))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("[Main] Finished stress test for filter_text.")
    print("[Main] Starting stress test for get_filtered_results.")

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=stress_test_get_filtered_results, args=(i, num_requests_per_thread))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("[Main] Finished stress test for get_filtered_results.")
    print(f"[Main] Total Requests: {num_threads * num_requests_per_thread * 4}")
    print(f"[Main] Average Latency: {mean(latencies):.5f} seconds")
    print(f"[Main] Total Errors: {errors}")

if __name__ == "__main__":
    run_stress_test()