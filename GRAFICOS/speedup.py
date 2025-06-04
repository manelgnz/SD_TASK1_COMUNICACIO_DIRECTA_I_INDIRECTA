import matplotlib.pyplot as plt

# Gráfico de barras para comparar el tiempo total de procesamiento de 2,000 peticiones

tecnologias = ['Pyro', 'Redis', 'RabbitMQ']
tiempos = [2.13, 2.46, 2.68]  

colores = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Azul, naranja, verde

plt.figure(figsize=(8, 5))
plt.bar(tecnologias, tiempos, color=colores)
plt.title('Speedup')
plt.xlabel('Tecnología')
plt.ylabel('T1/TN')
plt.grid(axis='y')
plt.tight_layout()
plt.show()