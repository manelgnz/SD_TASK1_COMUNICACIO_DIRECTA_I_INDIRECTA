import redis
from insult_service import InsultService  # Assegura't de tenir la classe InsultService en aquest fitxer
from insult_filter import InsultFilter      # Assegura't de tenir la classe InsultFilter en aquest fitxer

# Inicialitzar serveis
insult_service = InsultService()
filter_service = InsultFilter()

# Menú interactiu
while True:
    print("\nMenú:")
    print("1. Afegir un insult")
    print("2. Mostrar tots els insults")
    print("3. Filtrar un missatge")
    print("4. Sortir")

    choice = input("Escull una opció (1-4): ")

    if choice == '1':
        insult = input("Escriu l'insult que vols afegir: ")
        insult_service.add_insult(insult)

    elif choice == '2':
        insults = insult_service.get_insults()  # Obtenir i mostrar tots els insults
        print("Insults emmagatzemats:", insults)

    elif choice == '3':
        text_to_filter = input("Escriu el missatge que vols filtrar: ")
        insults = insult_service.get_insults()  # Obtenir la llista d'insults
        filtered_message = filter_service.filter_message(text_to_filter, insults)
        print(f"Missatge filtrat: {filtered_message}")

    elif choice == '4':
        print("Sortint...")
        break  # Sortir del bucle

    else:
        print("Opció no vàlida. Si us plau, escull una opció del menú.")
