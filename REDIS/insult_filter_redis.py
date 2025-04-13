import redis
import multiprocessing

def worker_process(redis_config, task_queue, result_key):
    r = redis.Redis(**redis_config)
    while True:
        _, text = r.blpop(task_queue)
        insult_list = r.lrange('insult_list', 0, -1)  # recarga dinámica
        for insult in insult_list:
            text = text.replace(insult, 'CENSORED')
        r.rpush(result_key, text)


class InsultFilter:
    def __init__(self):
        self.redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True
        }
        self.r = redis.Redis(**self.redis_config)
        self.task_queue = 'filter_queue'
        self.result_key = 'filtered_results'
        self.insult_list = self.r.lrange('insult_list', 0, -1)

    def start_worker(self):
        p = multiprocessing.Process(
            target=worker_process,
            args=(self.redis_config, self.task_queue, self.result_key),
            daemon=True
        )
        p.start()


    def add_text(self, text: str):
        self.r.rpush(self.task_queue, text)

    def get_results(self):
        return self.r.lrange(self.result_key, 0, -1)

if __name__ == '__main__':
    import time
    filter_service = InsultFilter()
    filter_service.start_worker()
    filter_service.add_text("You fight like a dairy farmer!")
    time.sleep(2)
    print("Filtered:", filter_service.get_results())
