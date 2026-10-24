import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

NAVY = "#1F3864"
BLUE = "#2E5EAA"
LIGHT = "#D9E2F3"
GRAY = "#6B7280"
GREEN = "#2E7D32"
WHITE = "#FFFFFF"


def box(ax, x, y, w, h, text, fc=LIGHT, ec=NAVY, fontsize=10.5, fontweight="normal", tc="black", zorder=3):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                        linewidth=1.6, edgecolor=ec, facecolor=fc, zorder=zorder)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color=tc, zorder=zorder + 1, wrap=True)
    return b


def arrow(ax, xy1, xy2, color=GRAY, style="-|>", lw=1.8, connectionstyle="arc3,rad=0.0", ls="-"):
    a = FancyArrowPatch(xy1, xy2, arrowstyle=style, mutation_scale=16,
                         linewidth=lw, color=color, connectionstyle=connectionstyle,
                         linestyle=ls, zorder=2)
    ax.add_patch(a)


fig, ax = plt.subplots(figsize=(10.2, 7.0))
ax.set_xlim(0, 10.2)
ax.set_ylim(0, 7.0)
ax.axis("off")

ax.text(5.1, 6.72, "MCP Architecture Overview", ha="center", fontsize=15.5, fontweight="bold", color=NAVY)

host = FancyBboxPatch((0.4, 4.55), 9.4, 1.75, boxstyle="round,pad=0.02,rounding_size=0.08",
                       linewidth=1.6, edgecolor=NAVY, facecolor="#F2F5FB", zorder=1)
ax.add_patch(host)
ax.text(0.75, 6.05, "MCP Host  (AI Application, e.g. Claude Desktop / IDE / Custom Agent)",
        fontsize=10.8, fontweight="bold", color=NAVY, ha="left")

box(ax, 0.75, 4.75, 2.7, 1.0, "AI Model /\nAgent Reasoning", fc="#FFFFFF", fontweight="bold")
box(ax, 3.75, 4.9, 1.7, 0.7, "MCP Client 1", fc=LIGHT)
box(ax, 5.6, 4.9, 1.7, 0.7, "MCP Client 2", fc=LIGHT)
box(ax, 7.45, 4.9, 1.9, 0.7, "MCP Client 3", fc=LIGHT)
arrow(ax, (3.45, 5.25), (3.75, 5.25))
arrow(ax, (3.45, 5.1), (5.6, 5.1), connectionstyle="arc3,rad=-0.15")
arrow(ax, (3.45, 4.95), (7.45, 4.95), connectionstyle="arc3,rad=-0.25")

# Servers row
box(ax, 0.6, 2.55, 2.55, 1.1, "MCP Server A\n(Local · Filesystem)\nTransport: stdio", fc="#E7F0FF")
box(ax, 3.5, 2.55, 2.55, 1.1, "MCP Server B\n(Local · ERP DB)\nTransport: stdio", fc="#E7F0FF")
box(ax, 6.4, 2.55, 3.15, 1.1, "MCP Server C\n(Remote · SaaS API)\nTransport: Streamable HTTP + OAuth 2.1", fc="#E7F0FF")

arrow(ax, (4.6, 4.9), (1.9, 3.65), connectionstyle="arc3,rad=0.15")
arrow(ax, (6.45, 4.9), (4.8, 3.65), connectionstyle="arc3,rad=0.1")
arrow(ax, (8.4, 4.9), (8.0, 3.65), connectionstyle="arc3,rad=0.0")

ax.text(5.1, 2.25, "Data layer: JSON-RPC 2.0  |  initialize, tools/list, tools/call, resources/*, prompts/*",
        ha="center", fontsize=9.3, color=GRAY, style="italic")

# Primitives exposed
box(ax, 0.6, 0.9, 2.9, 1.05, "Tools\n(model-invoked actions)", fc="#FDECEA", ec="#B23A2E")
box(ax, 3.8, 0.9, 2.6, 1.05, "Resources\n(read-only context data)", fc="#EAF7EC", ec=GREEN)
box(ax, 6.7, 0.9, 2.85, 1.05, "Prompts\n(reusable templates)", fc="#FFF6E0", ec="#B98900")

for xc in [2.05, 5.1, 8.1]:
    arrow(ax, (xc, 2.55), (xc, 1.95), color=GRAY, lw=1.4)

plt.tight_layout()
plt.savefig("diagram_architecture.png", dpi=220, bbox_inches="tight")
plt.close()

fig, ax = plt.subplots(figsize=(10.2, 5.6))
ax.set_xlim(0, 10.2)
ax.set_ylim(0, 5.6)
ax.axis("off")

ax.text(5.1, 5.32, "Agent-Tool Interaction Flow (MCP)", ha="center", fontsize=15.5, fontweight="bold", color=NAVY)

steps = [
    ("1. AI Agent", "Decides it needs\nexternal capability", 0.35),
    ("2. MCP Client", "Sends tools/list,\nthen tools/call", 2.15),
    ("3. MCP Server", "Validates & routes\nthe request", 3.95),
    ("4. Tool / Resource", "Executes the\nrequested action", 5.75),
    ("5. External System", "DB / API / file /\nPython function", 7.55),
]
y = 3.55
w, h = 1.55, 1.35
for title, sub, x in steps:
    box(ax, x, y, w, h, f"{title}\n\n{sub}", fc=LIGHT, fontsize=9.2, fontweight="bold")

for i in range(len(steps) - 1):
    x1 = steps[i][2] + w
    x2 = steps[i + 1][2]
    arrow(ax, (x1, y + h / 2), (x2, y + h / 2), color=BLUE, lw=2.2)

return_y = 1.55
box(ax, 7.55, return_y, w, h, "6. Result", fc="#EAF7EC", ec=GREEN, fontsize=9.2, fontweight="bold")
box(ax, 0.35, return_y, w, h, "7. AI Agent\n\nUses result for\nnext decision", fc="#FDECEA", ec="#B23A2E", fontsize=9.2, fontweight="bold")

arrow(ax, (7.55 + w / 2, y), (7.55 + w / 2, return_y + h), color=GREEN, lw=2.2,
      connectionstyle="arc3,rad=0.0")
arrow(ax, (7.55, return_y + h / 2), (0.35 + w, return_y + h / 2), color="#B23A2E", lw=2.2,
      connectionstyle="arc3,rad=0.0")
arrow(ax, (0.35 + w / 2, return_y), (0.35 + w / 2 + 1.6, y),
      color=GRAY, lw=1.6, ls="--", connectionstyle="arc3,rad=-0.3")

ax.text(5.1, 0.55,
        "Loop: the AI Agent may issue further MCP tool/resource calls based on the returned result\n"
        "before producing a final response -- the same request/response cycle repeats per decision.",
        ha="center", fontsize=9.0, color=GRAY, style="italic")

plt.tight_layout()
plt.savefig("diagram_workflow.png", dpi=220, bbox_inches="tight")
plt.close()

print("diagrams written")
