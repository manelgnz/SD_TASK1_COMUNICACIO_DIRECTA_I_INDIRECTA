import time
import random
from InsultService_REDIS import InsultService

def generate_insults(n):
    """Genera insultos simulados"""
    return [f"Insult #{i} - You're slower than a snail!" for i in range(n)]

def test_add_insults(service, insults):
    print("\n🚀 Iniciando test de inserción de insultos...")
    start = time.time()
    for insult in insults:
        service.add_insult(insult)
    end = time.time()
    total = len(insults)
    print(f"✔️  {total} insultos insertados en {end - start:.2f} segundos")
    print(f"⚡️  Throughput: {total / (end - start):.2f} insults/sec")

if __name__ == '__main__':
    service = InsultService()
    insults = generate_insults(5000)

    # Test de inserción masiva
    test_add_insults(service, insults)
