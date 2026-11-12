#!/usr/bin/env python3
"""Integrate piecewise-linear molar heat capacities over 1/T."""

import argparse
import csv
import math
from bisect import bisect_left
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Trace:
    temperature: tuple
    capacity: tuple
    modeled: tuple

    def sample(self, t):
        i = bisect_left(self.temperature, t)
        if i < len(self.temperature) and self.temperature[i] == t:
            return self.capacity[i], self.modeled[i]
        if i == 0 or i == len(self.temperature):
            raise ValueError(f"{t:g} K is outside supplied data coverage")
        fraction = (t - self.temperature[i - 1]) / (self.temperature[i] - self.temperature[i - 1])
        cp = (1 - fraction) * self.capacity[i - 1] + fraction * self.capacity[i]
        return cp, self.modeled[i - 1] or self.modeled[i]


def finite(value, label):
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def read_traces(path, grouped, allow_modeled):
    rows = defaultdict(list)
    columns = {"temperature_K", "heat_capacity_J_mol_K", "source"}
    if grouped:
        columns.add("field_T")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not columns.issubset(reader.fieldnames or []):
            raise ValueError(f"{path.name}: required columns are {', '.join(sorted(columns))}")
        for line, row in enumerate(reader, 2):
            try:
                t = finite(row["temperature_K"], "temperature_K")
                cp = finite(row["heat_capacity_J_mol_K"], "heat_capacity_J_mol_K")
                field = finite(row["field_T"], "field_T") if grouped else None
                if t <= 0:
                    raise ValueError("temperature_K must be positive")
                source = row["source"]
                if source not in {"measured", "modeled"}:
                    raise ValueError("source must be measured or modeled")
                rows[field].append((t, cp, source == "modeled"))
            except ValueError as exc:
                raise ValueError(f"{path.name}, row {line}: {exc}") from exc
    if not rows:
        raise ValueError(f"{path.name}: no data rows")

    traces = {}
    for key, points in rows.items():
        label = f"{key:g} T" if grouped else "phonon"
        points.sort()
        if any(a[0] == b[0] for a, b in zip(points, points[1:])):
            raise ValueError(f"{path.name}: duplicate temperature in {label}")
        selected = [point for point in points if allow_modeled or not point[2]]
        if len(selected) < 2:
            raise ValueError(f"{path.name}: {label} requires at least two allowed points")
        traces[key] = Trace(*zip(*selected))
    return traces


def window(traces, start, end):
    lo = max(trace.temperature[0] for trace in traces)
    hi = min(trace.temperature[-1] for trace in traces)
    if start is not None:
        if start < lo:
            raise ValueError(f"requested start is below supplied overlap ({lo:g} K)")
        lo = start
    if end is not None:
        if end > hi:
            raise ValueError(f"requested end exceeds supplied overlap ({hi:g} K)")
        hi = end
    if not 0 < lo < hi:
        raise ValueError("no positive temperature interval in the supplied overlap")
    return lo, hi


def integrate_linear(a, b, ca, cb):
    """Integral of the linear interpolant of C divided by T on [a, b]."""
    u = (b - a) / a
    log = math.log1p(u)
    weight = u * (0.5 + u * (-1 / 3 + u / 4)) if u < 1e-5 else 1 - log / u
    return ca * log + (cb - ca) * weight


def grid_for(traces, bounds, ref, fields):
    lo, hi = bounds
    knots = sorted({lo, hi, *(t for trace in traces for t in trace.temperature if lo < t < hi)})
    extrema = set()
    for trace in fields:
        diff = [ref.sample(t)[0] - trace.sample(t)[0] for t in knots]
        for a, b, da, db in zip(knots, knots[1:], diff, diff[1:]):
            if (da < 0 < db) or (db < 0 < da):
                extrema.add(a + (b - a) * da / (da - db))
    return sorted(set(knots) | extrema)


def integrate_pair(grid, ref, field, phonon):
    sm_ref = sm_field = delta = 0.0
    cumulative_cp = cumulative_background = False
    a = grid[0]
    ref_a, ref_modeled = ref.sample(a)
    field_a, field_modeled = field.sample(a)
    ph_a, ph_modeled = phonon.sample(a) if phonon else (0.0, False)
    yield (a, sm_ref, sm_field, delta, 0, 0, 0, 0)
    for b in grid[1:]:
        ref_b, ref_b_modeled = ref.sample(b)
        field_b, field_b_modeled = field.sample(b)
        ph_b, ph_b_modeled = phonon.sample(b) if phonon else (0.0, False)
        interval_cp = ref_modeled or field_modeled or ref_b_modeled or field_b_modeled
        interval_background = ph_modeled or ph_b_modeled
        cumulative_cp |= interval_cp
        cumulative_background |= interval_background

        sm_ref += integrate_linear(a, b, ref_a - ph_a, ref_b - ph_b)
        sm_field += integrate_linear(a, b, field_a - ph_a, field_b - ph_b)
        delta += integrate_linear(a, b, ref_a - field_a, ref_b - field_b)
        yield (b, sm_ref, sm_field, delta, int(interval_cp), int(cumulative_cp),
               int(interval_background), int(cumulative_background))

        a, ref_a, field_a, ph_a = b, ref_b, field_b, ph_b
        ref_modeled, field_modeled, ph_modeled = ref_b_modeled, field_b_modeled, ph_b_modeled


def write_integrals(args, traces, phonon):
    if args.reference_field not in traces:
        raise ValueError("reference field has no input trace")
    ref = traces[args.reference_field]
    fields = sorted(set(traces) - {args.reference_field})
    if not fields:
        raise ValueError("include a reference field and at least one comparison field")

    background = [phonon] if phonon else []
    if args.mode == "common":
        selected = list(traces.values()) + background
        bounds = window(selected, args.start, args.end)
        common = grid_for(selected, bounds, ref, [traces[field] for field in fields])
        grids = {field: common for field in fields}
    else:
        grids = {}
        for field in fields:
            pair = [ref, traces[field]] + background
            try:
                bounds = window(pair, args.start, args.end)
            except ValueError as exc:
                raise ValueError(f"{field:g} T: {exc}") from exc
            grids[field] = grid_for(pair, bounds, ref, [traces[field]])

    header = ["reference_field_T", "field_T", "lower_limit_K", "temperature_K"]
    if not args.delta_only:
        header.extend(["Srel_reference_J_mol_K", "Srel_field_J_mol_K"])
    header.extend(["minus_delta_Srel_J_mol_K", "interval_uses_modeled_cp", "cumulative_uses_modeled_cp"])
    if not args.delta_only:
        header.extend(["interval_uses_modeled_phonon", "cumulative_uses_modeled_phonon"])
    if args.molar_mass is not None:
        header.append("minus_delta_Srel_J_kg_K")
    if args.molar_volume is not None:
        header.append("minus_delta_Srel_mJ_cm3_K")

    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for field, grid in grids.items():
            for result in integrate_pair(grid, ref, traces[field], phonon):
                values = (result[0], *result[3:6]) if args.delta_only else result
                row = [args.reference_field, field, grid[0], *values]
                if args.molar_mass is not None:
                    row.append(result[3] * 1000 / args.molar_mass)
                if args.molar_volume is not None:
                    row.append(result[3] * 1000 / args.molar_volume)
                writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cp", required=True, type=Path,
                        help="CSV: field_T, temperature_K, heat_capacity_J_mol_K, source")
    basis = parser.add_mutually_exclusive_group(required=True)
    basis.add_argument("--phonon", type=Path,
                       help="background CSV: temperature_K, heat_capacity_J_mol_K, source")
    basis.add_argument("--magnetic-input", action="store_true", help="input Cp CSV already contains Cm")
    basis.add_argument("--delta-only", action="store_true",
                       help="compute only field entropy differences, with a common background canceled")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--reference-field", type=float, default=0.0, help="reference field in tesla")
    parser.add_argument("--mode", choices=["common", "pairwise"], default="common")
    parser.add_argument("--start", type=float, help="lower integration limit in kelvin")
    parser.add_argument("--end", type=float, help="upper integration limit in kelvin")
    parser.add_argument("--allow-modeled", action="store_true",
                        help="include explicitly labeled modeled rows, including for the phonon background")
    parser.add_argument("--molar-mass", type=float, help="g/mol")
    parser.add_argument("--molar-volume", type=float, help="cm^3/mol")
    args = parser.parse_args()
    try:
        finite(args.reference_field, "reference field")
        for name in ("start", "end", "molar_mass", "molar_volume"):
            value = getattr(args, name)
            if value is not None and finite(value, name) <= 0:
                raise ValueError(f"{name} must be positive")
        if any(path and path.resolve() == args.output.resolve() for path in (args.cp, args.phonon)):
            raise ValueError("output must be different from input files")
        traces = read_traces(args.cp, grouped=True, allow_modeled=args.allow_modeled)
        phonon = read_traces(args.phonon, grouped=False, allow_modeled=args.allow_modeled)[None] if args.phonon else None
        write_integrals(args, traces, phonon)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
