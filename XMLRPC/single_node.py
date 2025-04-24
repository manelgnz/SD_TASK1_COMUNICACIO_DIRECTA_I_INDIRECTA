import time
import xmlrpc.client
from statistics import mean
from multiprocessing import Pool, Manager

# Performance metrics (shared across processes)
def init_globals(latencies_add, latencies_filter, errors_add, errors_filter):
    global latencies_add_insult, latencies_filter_text, errors_add_insult, errors_filter_text
    latencies_add_insult = latencies_add
    latencies_filter_text = latencies_filter
    errors_add_insult = errors_add
    errors_filter_text = errors_filter

# Stress test for InsultService: add_insult
def stress_test_add_insult_process(insult):
    try:
        local_server = xmlrpc.client.ServerProxy("http://localhost:8000/")  # Reuse the connection
        start_time = time.time()
        local_server.add_insult(insult)
        end_time = time.time()
        latencies_add_insult.append(end_time - start_time)
    except Exception:
        errors_add_insult.value += 1

# Stress test for InsultFilter: filter_text
def stress_test_filter_text_process(text):
    try:
        local_server = xmlrpc.client.ServerProxy("http://localhost:8001/")  # Reuse the connection
        start_time = time.time()
        local_server.filter_text(text)
        end_time = time.time()
        latencies_filter_text.append(end_time - start_time)
    except Exception:
        errors_filter_text.value += 1

# Run stress tests
def run_stress_test():
    num_requests = 1000  # Total number of requests for each test
    num_processes = 8  # Number of parallel processes

    # Shared lists and counters for multiprocessing
    with Manager() as manager:
        latencies_add_insult = manager.list()
        latencies_filter_text = manager.list()
        errors_add_insult = manager.Value('i', 0)
        errors_filter_text = manager.Value('i', 0)

        # Stress test for add_insult
        print("[Main] Starting stress test for add_insult.")
        insults = [f"Insult {i}" for i in range(num_requests)]
        start_time_add_insult = time.time()  # Start time for add_insult
        with Pool(processes=num_processes, initializer=init_globals, initargs=(latencies_add_insult, latencies_filter_text, errors_add_insult, errors_filter_text)) as pool:
            pool.map(stress_test_add_insult_process, insults)
        end_time_add_insult = time.time()  # End time for add_insult

        total_time_add_insult = end_time_add_insult - start_time_add_insult
        requests_per_second_add_insult = num_requests / total_time_add_insult

        print("[Main] Finished stress test for add_insult.")
        print(f"[Main] Total Requests for add_insult: {num_requests}")
        print(f"[Main] Average Latency for add_insult: {mean(latencies_add_insult):.5f} seconds")
        print(f"[Main] Total Errors for add_insult: {errors_add_insult.value}")
        print(f"[Main] Total Time for add_insult: {total_time_add_insult:.5f} seconds")
        print(f"[Main] Requests per Second for add_insult: {requests_per_second_add_insult:.2f} req/s")

        # Stress test for filter_text
        print("[Main] Starting stress test for filter_text.")
        texts = [f"This is a test with insult {i}" for i in range(num_requests)]
        start_time_filter_text = time.time()  # Start time for filter_text
        with Pool(processes=num_processes, initializer=init_globals, initargs=(latencies_add_insult, latencies_filter_text, errors_add_insult, errors_filter_text)) as pool:
            pool.map(stress_test_filter_text_process, texts)
        end_time_filter_text = time.time()  # End time for filter_text

        total_time_filter_text = end_time_filter_text - start_time_filter_text
        requests_per_second_filter_text = num_requests / total_time_filter_text

        print("[Main] Finished stress test for filter_text.")
        print(f"[Main] Total Requests for filter_text: {num_requests}")
        print(f"[Main] Average Latency for filter_text: {mean(latencies_filter_text):.5f} seconds")
        print(f"[Main] Total Errors for filter_text: {errors_filter_text.value}")
        print(f"[Main] Total Time for filter_text: {total_time_filter_text:.5f} seconds")
        print(f"[Main] Requests per Second for filter_text: {requests_per_second_filter_text:.2f} req/s")

if __name__ == "__main__":
    run_stress_test()