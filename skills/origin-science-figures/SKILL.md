---
name: origin-science-figures
license: MIT
description: Create, restyle, or audit editable Origin/OriginPro scientific figures, especially dual-Y heat-capacity, entropy, and magnetocaloric plots. Use for data rebinding, baseline and extrapolation checks, axis conversions, and publication export.
---

# Origin Science Figures

Use the user's existing Origin graph as the style reference when available. Identify the active plot, its worksheet X/Y bindings, axis layers, and actual displayed data before changing anything. Work from a copy of the project and preserve raw inputs, user annotations, and existing graphs outside the requested edit. Keep numerical changes traceable separately from presentation changes.

## Choose the numerical scope

- For a formatting request, retain the underlying values and verify the plotted bindings after editing.
- For a recalculation, record each series' measured temperature range, units, baseline, and processing provenance. Clarify whether a shared starting point means the same plotted temperature, the same integral lower limit, or the same numerical reference value.
- For heat capacity, magnetic entropy, or magnetocaloric entropy change, read [the entropy methods](references/entropy.md) before calculating. The bundled [integration script](scripts/integrate_entropy.py) accepts explicitly prepared molar heat capacities, handles different grids, and records intervals that use supplied model points.

## Reuse the layout

1. Duplicate the selected graph or import a clean graph template. Rebind both X and Y for each series. Check plot type, line and symbol properties, legend order, layer assignment, row limits, and symbol skipping. Rebind auxiliary plots and labels that depend on data.
2. Match the reference at its intended output size. Preserve line-and-symbol or open-circle styles when requested, use color consistently across panels, and place the legend clear of curves and tick labels.
3. Choose the secondary axis based on its meaning. A unit conversion must transform the same ticks deterministically. Two independent quantities need two Y scales and a shared X axis. See [Origin setup and export](references/origin.md).
4. Make extrapolation visible with line style or a clear caption and keep flags in the worksheet. Styling a modeled segment as a solid line leaves its contribution in any subsequent cumulative integral.

## Verify the deliverables

- Check first and last plotted points, peak positions, axis conversions, signs, units, legend bindings, and annotation heights against the worksheet. Set limits that contain all intended curves, including justified negative values.
- Reopen the editable project and render each final export at manuscript size. Check clipping, label spacing, line and symbol rendering, and the presence of real vector paths when delivering a vector file.
- Deliver the editable Origin project and requested exports. When numbers were changed, include the processed table and the assumptions needed to reproduce it.
