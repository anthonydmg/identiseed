import numpy as np
import matplotlib.pyplot as plt

# Parámetros de la recta en coordenadas polares
r0 = 1 / np.sqrt(2)
theta0 = np.pi / 4

# Rango de ángulos theta
theta = np.linspace(0, 2 * np.pi, 400)

# Ecuación de la recta en coordenadas polares
r = r0 / np.cos(theta - theta0)

# Gráfico en coordenadas polares
plt.figure(figsize=(8, 8))
ax = plt.subplot(111, projection='polar')
ax.plot(theta, r, label='r = r0 / cos(θ - θ0)')

# Configuración del gráfico
ax.set_title('Ecuación de una recta en coordenadas polares')
ax.legend(loc='upper right')
plt.show()