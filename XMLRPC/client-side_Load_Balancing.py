import xmlrpc.client
import time
from itertools import cycle
from statistics import mean

# List of InsultService nodes
insult_service_nodes = ["http://localhost:8000/", "http://localhost:8001/"]
insult_service_cycle = cycle(insult_service_nodes)  # Round-robin iterator

# List of InsultFilter nodes
insult_filter_nodes = ["http://localhost:9000/", "http://localhost:9001/"]
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

# Stress test
def stress_test(num_requests):
    insults = [f"Insult {i}" for i in range(num_requests)]
    texts = [f"This is a test with insult {i}" for i in range(num_requests)]

    # Metrics for add_insult
    latencies_add_insult = []
    errors_add_insult = 0

    # Test add_insult
    print("[Main] Starting stress test for add_insult.")
    start_time_add_insult = time.time()
    for insult in insults:
        latency = add_insult(insult)
        if latency is not None:
            latencies_add_insult.append(latency)
        else:
            errors_add_insult += 1
    end_time_add_insult = time.time()

    total_time_add_insult = end_time_add_insult - start_time_add_insult
    requests_per_second_add_insult = num_requests / total_time_add_insult if total_time_add_insult > 0 else 0
    print("[Main] Finished stress test for add_insult.")
    print(f"[Main] Total Requests for add_insult: {num_requests}")
    print(f"[Main] Average Latency for add_insult: {mean(latencies_add_insult):.5f} seconds" if latencies_add_insult else "[Main] No successful requests.")
    print(f"[Main] Total Errors for add_insult: {errors_add_insult}")
    print(f"[Main] Total Time for add_insult: {total_time_add_insult:.5f} seconds")
    print(f"[Main] Requests per Second for add_insult: {requests_per_second_add_insult:.2f} req/s")

    # Metrics for filter_text
    latencies_filter_text = []
    errors_filter_text = 0

    # Test filter_text
    print("[Main] Starting stress test for filter_text.")
    start_time_filter_text = time.time()
    for text in texts:
        latency = filter_text(text)
        if latency is not None:
            latencies_filter_text.append(latency)
        else:
            errors_filter_text += 1
    end_time_filter_text = time.time()

    total_time_filter_text = end_time_filter_text - start_time_filter_text
    requests_per_second_filter_text = num_requests / total_time_filter_text if total_time_filter_text > 0 else 0
    print("[Main] Finished stress test for filter_text.")

    
    print(f"[Main] Total Requests for add_insult: {num_requests}")
    print(f"[Main] Average Latency for add_insult: {mean(latencies_add_insult):.5f} seconds" if latencies_add_insult else "[Main] No successful requests.")
    print(f"[Main] Total Errors for add_insult: {errors_add_insult}")
    print(f"[Main] Total Time for add_insult: {total_time_add_insult:.5f} seconds")
    print(f"[Main] Requests per Second for add_insult: {requests_per_second_add_insult:.2f} req/s")

    print(f"[Main] Total Requests for filter_text: {num_requests}")
    print(f"[Main] Average Latency for filter_text: {mean(latencies_filter_text):.5f} seconds" if latencies_filter_text else "[Main] No successful requests.")
    print(f"[Main] Total Errors for filter_text: {errors_filter_text}")
    print(f"[Main] Total Time for filter_text: {total_time_filter_text:.5f} seconds")
    print(f"[Main] Requests per Second for filter_text: {requests_per_second_filter_text:.2f} req/s")

if __name__ == "__main__":
    stress_test(100)  # Number of requests