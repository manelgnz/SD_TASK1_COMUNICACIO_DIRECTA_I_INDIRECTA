import Pyro4
import random
import time

# Connexió al servei
filter_service = Pyro4.Proxy("PYRONAME:InsultFilterService")

# Insults coneguts del servei
known_insults = [
    "You are a fool",
    "Your brain is like a sieve",
    "Get a life",
    "You're a genius, just kidding!"
]

# Textos neutres
neutral_phrases = [
    "Have a great day!",
    "Let's meet at 5.",
    "This is a simple message.",
    "Good morning!",
    "No insults here!"
]

# Funció per generar textos aleatoris
def generate_random_text():
    if random.random() < 0.5:  # 50% de possibilitat de contenir insult
        return f"This message contains: {random.choice(known_insults)}"
    else:
        return random.choice(neutral_phrases)

# Enviem 100 textos
start_time = time.time()
for i in range(1000):
    text = generate_random_text()
    filtered = filter_service.filter_text(text)
    print(f"[{i+1:03}] Original: {text}")
    print(f"      Filtered: {filtered}\n")
end_time = time.time()

print("✅ Stress test completed.")
print(f"⌛ Total time: {end_time - start_time:.2f} seconds")

# Recuperem els resultats per verificar
print("\n📝 Filtered Results (first 10):")
results = filter_service.get_filtered_results()
for r in results[:10]:
    print("•", r)

print(f"\n📊 Total filtered messages stored: {len(results)}")
