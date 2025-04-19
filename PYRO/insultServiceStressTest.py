import Pyro4
import random
import time

# Connexió al servei
insult_service = Pyro4.Proxy("PYRONAME:InsultService")

# Insults de prova (barreja d'insults nous i alguns duplicats)
test_insults = [
    "You are a fool",
    "You are a genius!",
    "Your brain is like a sieve",
    "You are a genius!",  # Duplicat
    "You are invisible!",
    "You're a genius, just kidding!",
    "Get a life",
    "Get a life",  # Duplicat
    "Go learn some manners.",
    "You are a genius!"  # Duplicat
]

# Genera 100 insults aleatoris per enviar
insults_to_send = [random.choice(test_insults) for _ in range(1000)]

# Enviar insults
start = time.time()
added = 0
for i, insult in enumerate(insults_to_send):
    result = insult_service.add_insult(insult)
    if result:
        added += 1
    print(f"[{i+1:03}] Sent: {insult} | {'✅ Added' if result else '❌ Duplicate'}")

end = time.time()
print("\n✅ Stress test completed.")
print(f"⌛ Time taken: {end - start:.2f} seconds")
print(f"➕ New insults added: {added}")
print(f"📊 Total unique insults now: {len(insult_service.get_insults())}")
