import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 10))

# Function to create a text box
def create_box(ax, text, xy, width=2.5, height=1, boxstyle="round,pad=0.3", facecolor="wheat", edgecolor="black"):
    ax.add_patch(
        patches.FancyBboxPatch(
            xy, width=width, height=height, boxstyle=boxstyle, facecolor=facecolor, edgecolor=edgecolor
        )
    )
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=12)

# Function to create an arrow
def create_arrow(ax, start, end):
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.5))

# Define positions
start_pos = (5, 18)
decision_pos = (5, 16)
case_positions = {
    "case 1: Monday": (1, 13),
    "case 2: Tuesday": (5, 13),
    "case 3: Wednesday": (9, 13),
    "case 4: Thursday": (1, 10),
    "case 5: Friday": (5, 10),
    "case 6: Saturday": (9, 10),
    "case 7: Sunday": (5, 7),
    "default: Invalid": (5, 4),
}
stop_pos = (5, 1)

# Create boxes
create_box(ax, "Start", start_pos, facecolor="lightgreen")
create_box(ax, "n", decision_pos, width=2, height=2, boxstyle="round,pad=0.3", facecolor="lightblue")
for case, pos in case_positions.items():
    create_box(ax, case, pos, facecolor="lightyellow")
create_box(ax, "Stop", stop_pos, facecolor="lightgreen")

# Create arrows
create_arrow(ax, (6.25, 18), (6.25, 16.5))
create_arrow(ax, (6, 16), (2.5, 13.5))
create_arrow(ax, (6, 16), (6.25, 13.5))
create_arrow(ax, (6, 16), (9.25, 13.5))
create_arrow(ax, (6, 16), (2.5, 10.5))
create_arrow(ax, (6, 16), (6.25, 10.5))
create_arrow(ax, (6, 16), (9.25, 10.5))
create_arrow(ax, (6, 16), (6, 7.5))
create_arrow(ax, (6, 16), (6, 4.5))

# Arrows from cases to stop
for pos in case_positions.values():
    create_arrow(ax, (pos[0] + 1.25, pos[1]), (6.25, 1.5))

# Set limits and remove axes
ax.set_xlim(0, 12)
ax.set_ylim(0, 20)
ax.axis('off')

# Display the diagram
plt.show()