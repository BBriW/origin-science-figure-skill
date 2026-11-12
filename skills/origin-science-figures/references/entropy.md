# Heat capacity and magnetic entropy

## Select the reference

For a common molar phonon heat capacity, use `Cm(T,H) = Cp(T,H) - Cph(T)` and define the relative entropy at the chosen lower limit `T0`:

```text
Srel(T,H; T0) = integral from T0 to T of Cm(t,H)/t dt
-DeltaSrel(T; Href -> H) = Srel(T,Href; T0) - Srel(T,H; T0)
```

The two branches of each difference must use the same lower limit. For comparable field changes, use the same lower limit for every field. If you use a separate common measured range for each reference/field pair, document its limits. Different lower limits omit different amounts of entropy and can change peak heights, ordering, and signs.

A common lower limit gives zero at that point for all **relative** integrals. An absolute or third-law reference needs a justified contribution below the lowest usable measured temperature and a stated residual-entropy assumption. Add it explicitly and only to the branches for which it is estimated. An unexplained offset or a high-temperature target cannot establish the low-temperature entropy by itself.

An isothermal magnetization method is a different route. In the Maxwell approach, the integral is over field, using temperature differences of adjacent magnetization isotherms. The temperature plotted for a finite difference is commonly the midpoint of the paired isotherms. It is distinct from the lower limit of an integral of `Cm/T`.

## Build and integrate the inputs

- Sort by temperature, check units and calibration factors, resolve duplicate temperatures explicitly, and inspect gaps or overlaps around splices before interpolation. Preserve raw values separately. Confirm whether a background is already subtracted.
- Use the measured intersection when the comparison should be free of heat-capacity extrapolation. For a requested lower limit outside that intersection, use a model supported by the data and physics of the sample. Record the fit window, parameters, join point, and modeled temperature interval. Avoid extending a high-order interpolant beyond its data. Check how another plausible model changes the low-temperature integral.
- Interpolate onto a grid containing the original knots and the exact integration bounds. If you use trapezoids, integrate `Cm/T` against **temperature**, including the actual spacing. The bundled script instead integrates each piecewise-linear heat-capacity segment over `1/T` analytically. Use the same convention for all fields.
- Preserve the sign of the heat capacity and entropy change. Investigate negative observations against the raw signal, addenda, units, and background rather than clipping them. Plot flags distinguish modeled input from measurements. Any modeled low-temperature interval contributes to the integral at subsequent temperatures, including where both input curves are measured.
- With the same background in both fields, it cancels in `-DeltaSrel`. Cross-check against the direct integral of `[Cp(T,Href)-Cp(T,H)]/T`. The background remains necessary for each field's magnetic entropy. The numerical helper’s `--delta-only` mode leaves those columns out.
- Select peaks in the requested window, checking endpoints. Within a piecewise-linear model, extrema can occur at a zero crossing of the heat-capacity difference. Retain enough temperature precision to preserve sharp features.

## Convert and label

If `S_mol` is in J mol⁻¹ K⁻¹, the sample molar mass is `M` in g mol⁻¹, and its molar volume is `V_m` in cm³ mol⁻¹:

- `S_mass = 1000 S_mol / M` in J kg⁻¹ K⁻¹.
- `S_volume = 1000 S_mol / V_m` in mJ cm⁻³ K⁻¹.
- Equivalently `S_volume = rho S_mass` for density `rho` in g cm⁻³.
- A ratio to a reference such as `R ln(g)` is dimensionless. State the degeneracy and the mole basis. Apply the same ratio to tick labels, annotations, and legend text.

Keep the entropy reference temperature in the axis title, caption, or method notes. Use the field endpoints in the entropy-change legend, and distinguish a magnetic field from a field change.
