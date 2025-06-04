import matplotlib.pyplot as plt

# Tecnologías y sus capacidades (mensajes por segundo)
tecnologias = ['XML-RPC', 'Pyro', 'Redis', 'RabbitMQ']
capacidades = [1, 690, 410, 2300]  # Ejemplo de valores, cámbialos por los reales si los tienes

colores = ['#9467bd', '#1f77b4', '#ff7f0e', '#2ca02c']  # Diferentes colores para cada barra

plt.figure(figsize=(8, 5))
plt.bar(tecnologias, capacidades, color=colores)
plt.title('Capacidad de procesamiento (msg/s) por tecnología')
plt.xlabel('Tecnología')
plt.ylabel('Mensajes por segundo')
plt.grid(axis='y')
plt.tight_layout()
plt.show()