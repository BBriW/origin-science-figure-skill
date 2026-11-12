# Origin Science Figure Skill

An Agent Skill for making editable, publication-ready figures in Origin/OriginPro. It covers two-Y-axis layout, transferring graph formatting to new datasets, checking unit conversions, and calculating relative magnetic entropy and magnetocaloric entropy change from heat capacity.

- **Keep your graph style.** Reuse an Origin page, rebind X/Y data, and verify legends, symbols, and ranges.
- **Make the baseline explicit.** Use a common measured interval or document modeled intervals and pairwise limits.
- **Check the exported figure.** Verify both axes, peak coordinates, signs, clipping, and the editable project.

## Install

Download or clone this repository. Copy the whole `skills/origin-science-figures` folder into `.agents/skills/` in your Codex project, or into `~/.agents/skills/` for all projects. Start a new session if the skill does not appear. [Codex skill installation](https://developers.openai.com/api/reference/cli)

### Example prompt

> Use $origin-science-figures to restyle my Origin dual-Y figure. Keep the current data and layout, verify both axis units, and export a vector PDF and editable Origin project.

The workflow uses an available Origin installation for native project edits. The numerical helper uses only the standard library and runs with Python 3.9 or newer. On Windows, use the Python launcher (such as `py -3`) or the path to an installed interpreter if `python` is unavailable.

## Run the synthetic example

Run this from the repository root.

```bash
python skills/origin-science-figures/scripts/integrate_entropy.py --cp examples/synthetic_cp.csv --phonon examples/synthetic_phonon.csv --output entropy.csv
```

The example has staggered temperature grids and an invented background. The common measured window is **3–6.5 K**, and the output starts at zero for each field change. At 6.5 K the synthetic 0→2 T result is `2.8 + 0.8 ln(6.5/3)` J mol⁻¹ K⁻¹. The helper includes exact crossings of the interpolated heat-capacity difference in the output grid, so candidate extrema can be checked without a fixed sampling step.

- `--mode pairwise` uses each reference/field pair's overlap instead of one interval for all fields.
- `--start` and `--end` select bounds within the supplied coverage. By default modeled rows are excluded and the remaining measured knots are interpolated linearly. Check large internal temperature gaps before accepting the interpolation. `--allow-modeled` admits explicitly supplied model rows and labels the affected intervals and cumulative values.
- `--magnetic-input` is available for already-subtracted magnetic heat capacity. When only total heat capacity is available and the same background applies to all fields, use `--delta-only` for entropy differences without per-field magnetic entropy. Optional `--molar-mass` and `--molar-volume` add mass and volume columns. See `--help` for the CSV schema and flags.

To make a dual-Y figure from the demo, rerun it with the synthetic conversion factors `--molar-mass 200 --molar-volume 50`. Import the output into Origin, split the rows by `field_T`, and plot `minus_delta_Srel_J_kg_K` against `temperature_K`. Show the right Y axis with tick-label formula `4*x`. A left-axis tick of 5 J kg⁻¹ K⁻¹ should then read 20 mJ cm⁻³ K⁻¹ on the right. The example conversion factors apply only to the synthetic demo.

The sample data are synthetic and intended for software validation. [Skill instructions](skills/origin-science-figures/SKILL.md) · [Numerical methods](skills/origin-science-figures/references/entropy.md) · [Origin setup](skills/origin-science-figures/references/origin.md)

### 中文用法

将 `skills/origin-science-figures` 文件夹复制到项目的 `.agents/skills/`，然后在 Codex 中调用 `$origin-science-figures`。示例使用合成数据，适合练习双 Y 轴、换单位和检查积分起点。

If the skill helps with your figures, use **Star** at the top of the repository to save it and help others discover it.

[MIT license](LICENSE)
