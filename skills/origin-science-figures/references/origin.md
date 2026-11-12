# Origin graph setup and export

## Rebind a graph without losing its format

Duplicate the page or work in a copy of the project. In Plot Setup or Plot Details, identify the plot's current X and Y columns and assign the new pair. A graph template can keep style properties and still carry old bindings, row limits, or legend references. Compare the first and last rendered coordinates with the new worksheet. The legend should reference the visible plots in the intended order.

For the helper’s long-format CSV, group rows by `field_T` and make a separate XY plot for each field. Use `temperature_K` as X. In a heat-capacity and entropy plot, keep the original heat-capacity temperature knots on the left and use the processed entropy temperatures on the right. The reference entropy is repeated for each field pair, so plot it once on a common grid or label it with the pair’s lower limit when the grid is pairwise.

For a line-and-symbol result, verify the plot type as well as symbol size and interior. Separate measured and modeled traces only when they require different styles. Give the two pieces the same color and an identical join coordinate. Use point spacing and symbol skipping to control visual density. Keep the underlying curve and its knots, including narrow peaks. Check for inherited Speed Mode or a skip interval that makes markers sparse in the export. [Origin graphing and Speed Mode](https://docs.originlab.com/user-guide/graphing/)

## Two kinds of dual Y axis

| Use case | Origin setup | Verification |
|---|---|---|
| One quantity in two units | Show both Y axes on the same layer and use a tick-label formula on the secondary side. For a linear conversion `y_right = k y_left` use `x*k` in Origin's tick-label formula, where `x` means the tick value. Use either a formula or a divide factor unless both are intentional. | Compare zero, one interior tick, and an endpoint with the conversion. Set display precision without rounding the stored factor. |
| Two different quantities | Assign each dataset to its own Y scale. In Origin 2023 or newer, assign the plot to the right Y axis in Plot Details → Display and check the axis assignment in Object Manager. In older projects, overlay aligned layers, link their X axes 1:1, and leave their Y scales independent. | Verify that rescaling one Y axis does not change the other's data coordinates, and both layers share the same X range. |

Use consistent typography, line weights, and legend order in related panels. Unit conversion must apply to labels and data markers together. For example, do not place an annotation in molar units on a normalized axis without transforming its Y position. An annotation tied to an event should use its computed coordinate on the owning layer.

[Origin Double-Y tutorial](https://docs.originlab.com/tutorials/double-y/) · [Origin tick-label display and formulas](https://docs.originlab.com/quick-help/format-axis-tick-labels/)

## Save and inspect

Keep the editable Origin project. Export vector PDF when the publisher accepts it and PNG or TIFF at the requested size for raster delivery. Menu names, automation properties, and available formats depend on Origin version. A Windows installation with Origin's official Python bridge can automate the workflow. Without Origin access, describe the limitation when delivering an export made by another tool. [Origin external Python](https://www.originlab.com/doc/ExternalPython)

Render the final files, ideally at placement size. Confirm axis titles and ticks fit, curves do not get truncated, symbols are visible, text is legible, and a vector export retains vector strokes. On reopen, verify that Origin still links the correct columns and renders all intended points. If the user will share a project publicly, inspect its worksheets, notes, links, attachments, and export metadata for unintended content.
