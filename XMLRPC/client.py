import xmlrpc.client

# Connect to InsultService
insult_service = xmlrpc.client.ServerProxy("http://localhost:8000/")

# Add insults to the InsultService
print("Adding insults to InsultService...")
insult_service.add_insult("idiot")
insult_service.add_insult("stupid")
insult_service.add_insult("fool")
print("Current insults:", insult_service.get_insults())

# Subscribe to the insult broadcaster (simulated URL for demonstration)
insult_service.subscribe("http://localhost:9000/")

# Connect to InsultFilter
insult_filter = xmlrpc.client.ServerProxy("http://localhost:8001/")

# Set insults in the InsultFilter
print("Setting insults in InsultFilter...")
insult_filter.set_insults(insult_service.get_insults())

# Filter some texts
print("Filtering texts...")
filtered_text1 = insult_filter.filter_text("You are an idiot!")
filtered_text2 = insult_filter.filter_text("This is a stupid idea.")
filtered_text3 = insult_filter.filter_text("No insults here.")
print("Filtered texts:", insult_filter.get_filtered_texts())

# Retrieve filtered texts
print("Retrieving all filtered texts...")
print(insult_filter.get_filtered_texts())