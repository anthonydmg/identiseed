import plotly.graph_objects as go
import numpy as np

# Ejemplo de datos
x = np.linspace(400, 900, 100)
fig = go.Figure()

for i in range(15):
    y = np.sin(x / 100 + i) * 20 + 40 + i
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f'semilla-{i}'))

fig.update_layout(
    xaxis_title='Wavelength',
    yaxis_title='Radiance',
    legend_title='Semillas',
)

fig.show()