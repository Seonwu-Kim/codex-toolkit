# Visualization Guide

Use this guide only when a PDF needs diagrams, timelines, Gantt charts, or
quantitative charts.

## Tool Selection

| Need | Preferred tool | Template |
| --- | --- | --- |
| Architecture, flow, sequence, ERD | Mermaid | `architecture.mmd` |
| Project schedule or Gantt | Mermaid Gantt | `gantt.mmd` |
| Dense dependency graph or exact port routing | Graphviz | `dependency.dot` |
| Quantitative chart | Vega-Lite | `chart.vl.json` |
| Pixel-level bespoke artwork | custom SVG, last resort | none |

Use Mermaid first for ordinary report diagrams. Use Graphviz when edge routing
or explicit node ports matter. Use Vega-Lite for data rather than drawing
charts manually.

## Dependencies

Install Mermaid and Vega-Lite locally inside the skill:

```bash
npm install --prefix <skill-dir> @mermaid-js/mermaid-cli
npm install --prefix <skill-dir> vega vega-lite vega-cli
```

Install Graphviz as an operating-system package:

```bash
# macOS
brew install graphviz

# Ubuntu / Debian
sudo apt-get install graphviz
```

The renderer also honors `MMDC`, `DOT`, and `VL2SVG` environment variables.

## Render

Copy a template to the document work directory, edit its labels or data, then
render SVG:

```bash
python scripts/render_visual.py \
  --type mermaid \
  --input work/architecture.mmd \
  --output work/architecture.svg

python scripts/render_visual.py \
  --type graphviz \
  --input work/dependency.dot \
  --output work/dependency.svg

python scripts/render_visual.py \
  --type vega-lite \
  --input work/chart.vl.json \
  --output work/chart.svg
```

Embed the SVG in Markdown and place a meaningful caption below it.

## Diagram Rules

- Keep one dominant reading direction and enough whitespace for edge labels.
- End arrows at node boundaries. Never let an arrowhead appear inside a node.
- Use different connection points for opposing inbound and outbound edges.
- Keep action labels outside nodes and away from crossings.
- Split a crowded visual into multiple diagrams instead of shrinking it.
- Use color as reinforcement, never as the only status indicator.
- Do not expose 제작 지침, agent notes, coordinates, or layout explanations in
  the published document.
- Prefer Mermaid or Graphviz over custom SVG.
- If custom SVG is unavoidable, put the arrow marker on a separate final
  straight segment rather than on a cornered polyline.

## Gantt Rules

- Use absolute dates and state the reporting timezone when time matters.
- Separate baseline, actual or forecast, and milestone semantics.
- Keep task names concise; put owner and variance details in a nearby table.
- Mark completion with text as well as color.
- Do not imply precision that the source schedule does not provide.

## Data Chart Rules

- Show metric name, unit, period, and data source.
- Label axes and use a zero baseline when magnitude comparison requires it.
- Avoid 3D charts, decorative gradients, and legends that repeat direct labels.
- Use tables when there are too few data points for a chart to clarify.

## Visual Verification

After building the PDF:

1. Inspect the full page at normal size.
2. Inspect every diagram at 200% zoom.
3. Check arrow origins, arrowheads, edge crossings, labels, clipping, and font
   rendering.
4. Confirm the caption describes meaning rather than drawing mechanics.
5. Re-render after every meaningful diagram change.
