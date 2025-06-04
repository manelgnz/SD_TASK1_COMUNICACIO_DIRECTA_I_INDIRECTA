XMLRPC

python insult_service.py --port 8000
python insult_service.py --port 8001
python insult_service.py --port 8002

python client-test.py

PYRO

python -m Pyro4.naming
python client_test.py

python worker.py worker.uno
python worker.py worker.dos
...

REDIS

python insult_service.py 
python insult_filter.py
python cliente.py
python cliente_insult_filter.py

//if you want to run more workers (services or filters), modify the variable num_workers in each file, due to we
used library multiprocessing 

RABBITMQ

python client_service.py
python client_filter.py
python insult_filter.py
python insult_service.py

//if you want to run more workers (services), open another cli


// to do dynamic scaling 
// don't run python insult_service.py
python dynamic_scaling.py
