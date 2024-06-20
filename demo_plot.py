import matplotlib.pyplot as plt
import numpy as np

# Datos de ejemplo (nombres y estaturas)
nombres = ['Persona A', 'Persona B', 'Persona C', 'Persona D', 'Persona E',
           'Persona F', 'Persona G', 'Persona H', 'Persona I', 'Persona J']
estaturas = [165, 170, 155, 180, 168, 172, 160, 175, 185, 162]

# Colores para cada punto
colores = np.arange(len(nombres))

# Crear el gráfico de dispersión (scatter plot)
plt.figure(figsize=(10, 6))  # Definir tamaño del gráfico (opcional)
scatter = plt.scatter(range(1, len(nombres) + 1), estaturas, c=colores, cmap='viridis', label=nombres)

# Añadir leyenda con colores
plt.legend(handles=scatter.legend_elements()[0], labels=nombres, loc='upper left', bbox_to_anchor=(1, 1))

print(scatter.legend_elements()[0])
# Añadir etiquetas y título
plt.title('Estaturas de Personas')
plt.xlabel('Personas')
plt.ylabel('Estatura (cm)')
plt.xticks(range(1, len(nombres) + 1), nombres, rotation=45, ha='right')

# Mostrar el gráfico
plt.tight_layout()
plt.show()