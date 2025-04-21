import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import time
from InsultService import InsultService  # Assuming InsultService is in the same directory

class InsultFilter:
    def __init__(self, insult_service):
        self.result_list = []
        self.insult_service = insult_service  # Reference to InsultService
        self.work_queue = []
        print("[InsultFilter] Initialized with an empty result list and work queue.")

    def filter_text(self, text):
        print(f"[InsultFilter] Filtering text: '{text}'")
        # Replace any insult in text with "CENSORED"
        for insult in self.insult_service.get_insults():
            if insult in text:
                print(f"[InsultFilter] Found insult '{insult}' in text. Replacing with 'CENSORED'.")
            text = text.replace(insult, "CENSORED")
        self.result_list.append(text)
        print(f"[InsultFilter] Filtered text: '{text}' added to result list.")
        return text

    def get_filtered_results(self):
        print(f"[InsultFilter] Returning filtered results: {self.result_list}")
        return self.result_list

    def add_to_work_queue(self, text):
        print(f"[InsultFilter] Adding text to work queue: '{text}'")
        self.work_queue.append(text)

    def process_queue(self):
        print("[InsultFilter] Starting to process the work queue...")
        while True:
            if self.work_queue:
                text = self.work_queue.pop(0)
                print(f"[InsultFilter] Processing text from work queue: '{text}'")
                self.filter_text(text)
            else:
                print("[InsultFilter] Work queue is empty. Waiting for new tasks...")
            time.sleep(1)

# XML-RPC server setup for InsultFilter
server = SimpleXMLRPCServer(("localhost", 8001), allow_none=True)
service = InsultFilter(insult_service=InsultService())  # Corrected initialization

server.register_function(service.filter_text, "filter_text")
server.register_function(service.get_filtered_results, "get_filtered_results")

# Start processing queue in a separate thread
threading.Thread(target=service.process_queue, daemon=True).start()

try:
    print("[InsultFilter] InsultFilter is running on port 8001...")
    server.serve_forever()
except KeyboardInterrupt:
    print("[InsultFilter] Shutting down InsultFilter...")
    server.server_close()