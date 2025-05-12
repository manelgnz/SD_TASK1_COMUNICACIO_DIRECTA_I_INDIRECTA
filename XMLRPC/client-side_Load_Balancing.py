import xmlrpc.client
import time
from itertools import cycle
from statistics import mean
from multiprocessing import Pool

# List of InsultService nodes
insult_service_nodes = ["http://localhost:8000/", "http://localhost:8001/", "http://localhost:8002/"]
insult_service_cycle = cycle(insult_service_nodes)  # Round-robin iterator

# List of InsultFilter nodes
insult_filter_nodes = ["http://localhost:9000/", "http://localhost:9001/", "http://localhost:9002/"]
insult_filter_cycle = cycle(insult_filter_nodes)  # Round-robin iterator

# Add insult using load balancing
def add_insult(insult):
    node = next(insult_service_cycle)  # Get the next node in the cycle
    server = xmlrpc.client.ServerProxy(node)
    try:
        start_time = time.time()
        response = server.add_insult(insult)
        end_time = time.time()
        return end_time - start_time  # Return latency
    except Exception as e:
        print(f"[Client] Error adding insult to {node}: {e}")
        return None  # Return None for errors

# Filter text using load balancing
def filter_text(text):
    node = next(insult_filter_cycle)  # Get the next node in the cycle
    server = xmlrpc.client.ServerProxy(node)
    try:
        start_time = time.time()
        response = server.filter_text(text)
        end_time = time.time()
        return end_time - start_time  # Return latency
    except Exception as e:
        print(f"[Client] Error filtering text on {node}: {e}")
        return None  # Return None for errors

# Multiprocessing wrapper for add_insult
def add_insult_wrapper(insult):
    return add_insult(insult)

# Multiprocessing wrapper for filter_text
def filter_text_wrapper(text):
    return filter_text(text)

# Stress test with multiprocessing
def stress_test_multiprocessing(num_requests, num_processes):
    insults = [f"Insult {i}" for i in range(num_requests)]
    texts = [f"This is a test with insult {i}" for i in range(num_requests)]

    # Test add_insult
    print("[Main] Starting multiprocessing stress test for add_insult.")
    start_time_add_insult = time.time()
    with Pool(processes=num_processes) as pool:
        latencies_add_insult = pool.map(add_insult_wrapper, insults)
    end_time_add_insult = time.time()

    total_time_add_insult = end_time_add_insult - start_time_add_insult
    successful_requests_add_insult = len([lat for lat in latencies_add_insult if lat is not None])
    requests_per_second_add_insult = successful_requests_add_insult / total_time_add_insult if total_time_add_insult > 0 else 0
    print("[Main] Finished multiprocessing stress test for add_insult.")
    print(f"[Main] Total Requests for add_insult: {num_requests}")
    print(f"[Main] Successful Requests for add_insult: {successful_requests_add_insult}")
    print(f"[Main] Average Latency for add_insult: {mean([lat for lat in latencies_add_insult if lat is not None]):.5f} seconds" if successful_requests_add_insult > 0 else "[Main] No successful requests.")
    print(f"[Main] Total Time for add_insult: {total_time_add_insult:.5f} seconds")
    print(f"[Main] Requests per Second for add_insult: {requests_per_second_add_insult:.2f} req/s")

    # Test filter_text
    print("[Main] Starting multiprocessing stress test for filter_text.")
    start_time_filter_text = time.time()
    with Pool(processes=num_processes) as pool:
        latencies_filter_text = pool.map(filter_text_wrapper, texts)
    end_time_filter_text = time.time()

    total_time_filter_text = end_time_filter_text - start_time_filter_text
    successful_requests_filter_text = len([lat for lat in latencies_filter_text if lat is not None])
    requests_per_second_filter_text = successful_requests_filter_text / total_time_filter_text if total_time_filter_text > 0 else 0
    print("[Main] Finished multiprocessing stress test for filter_text.")
    print(f"[Main] Total Requests for filter_text: {num_requests}")
    print(f"[Main] Successful Requests for filter_text: {successful_requests_filter_text}")
    print(f"[Main] Average Latency for filter_text: {mean([lat for lat in latencies_filter_text if lat is not None]):.5f} seconds" if successful_requests_filter_text > 0 else "[Main] No successful requests.")
    print(f"[Main] Total Time for filter_text: {total_time_filter_text:.5f} seconds")
    print(f"[Main] Requests per Second for filter_text: {requests_per_second_filter_text:.2f} req/s")

if __name__ == "__main__":
    stress_test_multiprocessing(num_requests=100, num_processes=10)  # Adjust num_requests and num_processes as needed