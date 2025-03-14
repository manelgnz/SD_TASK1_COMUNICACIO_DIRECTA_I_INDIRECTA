import redis
import time

client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
channel_name = "insult_channel"

# Publish multiple messages
insults = ["loser", "idiot", "stupid"]

while True:
    for insult in insults:
        client.publish(channel_name, insult)
        print(f"Published: {insult}")
        time.sleep(5)