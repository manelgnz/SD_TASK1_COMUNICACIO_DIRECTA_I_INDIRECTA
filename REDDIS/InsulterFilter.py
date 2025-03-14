import redis

client = redis.Redis(host='localhost', port=6379, db=0,
decode_responses=True)

queue_name = "task_queue"

print("Consumer is waiting for tasks...")

list_name = "resultsList"
insult_list = "insultList"

while True:
    task = client.blpop(queue_name, timeout=0) # Blocks indefinitely until a task is available
    if task:
        msg = task[1] # task[0] is the name of the list and task[1] is the value of the list
        if msg not in client.lrange(insult_list, 0, -1):
            client.rpush(list_name, msg)
            print(f"Message added to result List: {msg}")
        else:
            print(f"The message is an insult")
            client.rpush(list_name, "CENSORED")
            print(f"Message added to result List: CENSORED")