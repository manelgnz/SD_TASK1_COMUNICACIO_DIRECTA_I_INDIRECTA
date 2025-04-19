import time
from multiprocessing import Process
from InsultService_REDIS import InsultService
from uuid import uuid4
import redis

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
INSULTS_KEY = "insult_list"
INSULTS_SET_KEY = "insult_set"  # Set temporal para contar elementos únicos

# Worker function to add insults
def insult_worker(n):
    service = InsultService()  # Create an instance of InsultService
    for _ in range(n):
        insult = f"Benchmark Insult {uuid4()}"
        service.add_insult(insult)  # Use add_insult from InsultService

# Run multiple workers
def run_insult_workers(num_workers, insults_per_worker):
    print(f"\n[Benchmark] InsultService with {num_workers} process(es)...")

    # Clear insult list and set (to ensure clean slate)
    redis_client.delete(INSULTS_KEY)
    redis_client.delete(INSULTS_SET_KEY)

    processes = []
    start = time.time()

    # Create and start the worker processes
    for _ in range(num_workers):
        p = Process(target=insult_worker, args=(insults_per_worker,))
        p.start()
        processes.append(p)

    # Wait for all processes to complete
    for p in processes:
        p.join()

    elapsed = time.time() - start
    total_inserted = redis_client.llen(INSULTS_KEY)  # Count the total number of insults in the list
    unique_inserted = redis_client.scard(INSULTS_SET_KEY)  # Count the unique insults in the set
    print(f"Inserted {total_inserted} insults in the list in {elapsed:.2f} sec")
    print(f"{unique_inserted} unique insults were added in total (using set for uniqueness)")
    return elapsed

# Main function to run the benchmark
def main():
    insults_per_worker = 1000
    results = {}

    # Test for 1, 2, and 3 workers
    for workers in [1, 2, 3]:
        elapsed = run_insult_workers(workers, insults_per_worker)
        results[workers] = elapsed

    # Print speedup summary
    print("\n=== InsultService Speedup Summary ===")
    t1 = results[1]  # Time for single worker
    for n in [1, 2, 3]:
        speedup = t1 / results[n]  # Calculate speedup compared to single worker
        print(f"{n} worker(s): {results[n]:.2f} sec → Speedup: {speedup:.2f}x")

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
