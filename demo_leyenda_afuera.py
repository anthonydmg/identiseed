import matplotlib.pyplot as plt
import numpy as np

# Ejemplo de datos
x = np.linspace(400, 900, 100)
y = [np.sin(x / 100 + i) * 20 + 40 + i for i in range(15)]

fig, ax = plt.subplots()
for i, y_val in enumerate(y):
    ax.plot(x, y_val, label=f'semilla-{i}')

# Colocar la leyenda fuera del gráfico
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.xlabel('Wavelength')
plt.ylabel('Radiance')
plt.tight_layout()
plt.show()