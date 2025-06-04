import matplotlib.pyplot as plt

# Tecnologías y sus capacidades (mensajes por segundo)
tecnologias = ['XML-RPC', 'Pyro', 'Redis', 'RabbitMQ']
capacidades = [1, 0.00145, 0.0025, 0.00044]  # Ejemplo de valores, cámbialos por los reales si los tienes

colores = ['#9467bd', '#1f77b4', '#ff7f0e', '#2ca02c']  # Diferentes colores para cada barra

plt.figure(figsize=(8, 5))
plt.bar(tecnologias, capacidades, color=colores)
plt.title('Tiempo de procesamiento de un mensaje(s/msg) por tecnología')
plt.xlabel('Tecnología')
plt.ylabel('Tiempo por mensaje (segundos)')
plt.grid(axis='y')
plt.tight_layout()
plt.show()