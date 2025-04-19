import Pyro4

# Connecta't al servei registrat amb Pyro
filter_service = Pyro4.Proxy("PYRONAME:InsultFilterService")

# Envia textos al servei perquè els filtri
texts = [
    "Hello! You are a fool.",
    "Your brain is like a sieve and Get a life!",
    "No insult here.",
    "You're a genius, just kidding!"
]

for t in texts:
    filtered = filter_service.filter_text(t)
    print(f"Original: {t}")
    print(f"Filtered: {filtered}")
    print("-" * 40)

# Demana la llista de resultats filtrats
results = filter_service.get_filtered_results()
print("📝 All filtered results:")
for r in results:
    print("•", r)
