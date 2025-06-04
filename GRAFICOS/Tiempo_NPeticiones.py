import matplotlib.pyplot as plt

# Gráfico de barras para comparar el tiempo total de procesamiento de 2,000 peticiones

tecnologias = ['Pyro', 'Redis', 'RabbitMQ']
tiempos = [7.29, 13.23, 2.83]  # segundos

colores = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Azul, naranja, verde

plt.figure(figsize=(8, 5))
plt.bar(tecnologias, tiempos, color=colores)
plt.title('Tiempo total para procesar 5.000 peticiones')
plt.xlabel('Tecnología')
plt.ylabel('Tiempo (segundos)')
plt.grid(axis='y')
plt.tight_layout()
plt.show()


