import matplotlib.pyplot as plt

# Ejemplo de datos de escalado estático (puedes cambiarlos por tus valores reales)
nodos = [1, 2, 3]
pyro = [32, 18.8, 15]
redis = [128, 70, 52]
rabbitmq = [42, 20, 17]

plt.figure(figsize=(8, 5))
plt.plot(nodos, pyro, marker='o', color='#1f77b4', label='Pyro')
plt.plot(nodos, redis, marker='o', color='#ff7f0e', label='Redis')
plt.plot(nodos, rabbitmq, marker='o', color='#2ca02c', label='RabbitMQ')

plt.title('Escalado estático con 50.000 peticiones')
plt.xlabel('Número de nodos')
plt.ylabel('Tiempo de procesamiento (segundos)')
plt.xticks(nodos)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()