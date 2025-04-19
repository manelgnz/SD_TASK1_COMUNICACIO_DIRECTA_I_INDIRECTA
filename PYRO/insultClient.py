import Pyro4

# Connect to the InsultService and InsultFilterService
insult_service = Pyro4.Proxy("PYRONAME:InsultService")
filter_service = Pyro4.Proxy("PYRONAME:InsultFilterService")

def show_menu():
    print("\n💬 Client Menu")
    print("1. Add an insult to InsultService")
    print("2. Show list of insults from InsultService")
    print("3. Filter text using InsultFilterService")
    print("4. Show filtered results from InsultFilterService")
    print("5. Exit")

def add_insult():
    insult = input("🔤 Enter an insult to add: ")
    result = insult_service.add_insult(insult)
    if result:
        print("✅ Insult added successfully.")
    else:
        print("❌ This insult already exists.")

def show_insults_list():
    insults = insult_service.get_insults()
    print("\n📋 Current insults in InsultService:")
    for insult in insults:
        print(f"• {insult}")

def filter_text():
    text = input("🔤 Enter text to filter: ")
    filtered_text = filter_service.filter_text(text)
    print(f"\n📜 Filtered Text: {filtered_text}")

def show_filtered_results():
    filtered_texts = filter_service.get_filtered_results()
    print("\n📋 Filtered Texts from InsultFilterService:")
    for text in filtered_texts:
        print(f"• {text}")

def interactive_client():
    while True:
        show_menu()
        try:
            option = int(input("Select an option (1-5): "))
            if option == 1:
                add_insult()
            elif option == 2:
                show_insults_list()
            elif option == 3:
                filter_text()
            elif option == 4:
                show_filtered_results()
            elif option == 5:
                print("👋 Exiting...")
                break
            else:
                print("❌ Invalid option. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")

# Start interactive client
interactive_client()
