"""Offline exact Saturday comparison, isolated from historical reconstruction.

Run ``python -m riftbound_tickets.phase3a build|audit|figures|collect``.
Only collect uses the network, with immutable, separately indexed snapshots.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from .collectors.evidence import EvidenceStore
from .collectors.phase3a_sources import Phase3ASourceStore, archived_rules, collect_sources
from .collectors.schedules import schedule_rule
from .models.saturday_analytical import (
    VegasRules, binomial_probabilities, historical_metrics, historical_ticket_distribution,
    vegas_final_point_distribution, vegas_metrics, vegas_paths, vegas_ticket_distribution,
)
from .payouts.rules import SATURDAY_TIERS

NEW_CODE = (
    "src/riftbound_tickets/collectors/phase3a_sources.py",
    "src/riftbound_tickets/models/saturday_analytical.py",
    "src/riftbound_tickets/phase3a.py",
    "src/riftbound_tickets/charts/saturday_analytical.py",
)
TABLE_NAMES = (
    "saturday_analytical_comparison.csv", "saturday_ticket_distributions.csv",
    "saturday_vegas_paths.csv", "saturday_stage_probabilities.csv",
    "saturday_payout_thresholds.csv", "saturday_ticket_concentration.csv",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        raise ValueError("Empty analytical output")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def exact_fields(name: str, value: Fraction | int) -> dict:
    value = Fraction(value)
    return {name: float(value), name + "_exact": str(value)}


def rules_from_archive(root: Path) -> tuple[dict, VegasRules]:
    archived = archived_rules(root)
    if not archived["announcement_verification"]["verified_primary_announcement_content"]:
        raise ValueError("Preserved official eleventh-round statement could not be verified")
    if archived["published_capacity"] != 1024 or not archived["no_top_cut"]:
        raise ValueError("Unexpected Vegas capacity/cut; review official rules")
    rules = VegasRules(archived["day1_rounds"], archived["day2_rounds"],
                       archived["day2_minimum_match_points"],
                       tuple(tuple(t) for t in archived["point_tiers"]))
    return archived, rules


def historical_inputs(root: Path) -> tuple[list[dict], list[dict]]:
    rows = [r for r in read_csv(root / "outputs/tables/historical_ticket_economy.csv") if r["event_format"] == "saturday"]
    if len(rows) != 8:
        raise ValueError("Expected all eight historical Saturdays")
    store = EvidenceStore(root)
    records = [json.loads(line) for line in store.ledger.read_text().splitlines()]
    sources = []
    for row in rows:
        record = next(r for r in records if r["source_id"] == row["payout_source_id"] and r["url"] == row["payout_source_url"])
        rules = schedule_rule(store.read(record).decode(), "saturday")
        if rules["published_capacity"] != 512 or row["conditional_schedule_pool"] != "4992" or rules["rounds"] != 7:
            raise ValueError("Historical schedule differs from benchmark")
        if rules["tiers"] != [list(t) for t in SATURDAY_TIERS]:
            raise ValueError("Historical payout mismatch")
        sources.append(record)
    return rows, sources


def scenarios(historical: list[dict]) -> list[dict]:
    result = []
    for n in (256, 512, 1024):
        result.append({"scenario_id": f"equal-{n}", "scenario_kind": "hypothetical_equal_attendance",
                       "historical_n": n, "vegas_n": n, "observed_historical_event_key": "",
                       "historical_attendance_status": "hypothetical_beyond_published_cap" if n > 512 else "hypothetical_within_published_cap",
                       "vegas_attendance_status": "hypothetical_within_published_cap"})
    for row in historical:
        n = int(row["observed_n"])
        result.append({"scenario_id": "observed-" + row["event_key"], "scenario_kind": "observed_historical_field_matched_vegas_hypothesis",
                       "historical_n": n, "vegas_n": n, "observed_historical_event_key": row["event_key"],
                       "historical_attendance_status": "observed_over_advertised_cap_exception" if n > 512 else "observed_final_standings_field",
                       "vegas_attendance_status": "hypothetical_matched_historical_field"})
    result.append({"scenario_id": "published-full-caps", "scenario_kind": "published_capacity_comparison_not_attendance_forecast",
                   "historical_n": 512, "vegas_n": 1024, "observed_historical_event_key": "",
                   "historical_attendance_status": "hypothetical_full_published_capacity",
                   "vegas_attendance_status": "hypothetical_full_published_capacity"})
    return result


def analytical_tables(root: Path) -> tuple[dict[str, list[dict]], dict]:
    archived, rules = rules_from_archive(root)
    historical, old_sources = historical_inputs(root)
    comparisons, distributions, concentration = [], [], []
    for scenario in scenarios(historical):
        for split in (False, True):
            allocation = "reported_216_each_top8_scenario" if split else "official_placement"
            hmetrics = historical_metrics(scenario["historical_n"], split_top8=split)
            vmetrics = vegas_metrics(scenario["vegas_n"], rules)
            row = {**scenario, "historical_allocation": allocation,
                   "historical_published_capacity": 512, "vegas_published_capacity": 1024,
                   "basis": "analytical_equal_skill_no_draw_no_drop_not_physical_issuance",
                   "historical_pool_assumption": "all_128_awards_funded_4992_tickets",
                   "vegas_total_basis": "expected_total_not_maximum",
                   "vegas_rule_source_id": archived["source"]["source_id"]}
            observed = next((r for r in historical if r["event_key"] == scenario["observed_historical_event_key"]), None)
            row.update({"historical_observed_n_basis": observed["observed_n_basis"] if observed else "",
                        "historical_payout_source_url": observed["payout_source_url"] if observed else "all_eight_archived_schedules_see_sources_index",
                        "historical_payout_source_id": observed["payout_source_id"] if observed else ""})
            for prefix, metrics in (("historical_", hmetrics), ("vegas_", vmetrics)):
                for name, value in metrics.items():
                    row.update(exact_fields(prefix + name, value))
            comparisons.append(row)
            # Vegas is identical between historical allocation alternatives: emit once.
            pairs = [("historical", allocation, scenario["historical_n"], historical_ticket_distribution(scenario["historical_n"], split_top8=split))]
            if not split:
                pairs.append(("vegas", "official_match_points", scenario["vegas_n"], vegas_ticket_distribution(rules)))
            for model, variant, n, pmf in pairs:
                base = {"scenario_id": scenario["scenario_id"], "scenario_kind": scenario["scenario_kind"], "model": model,
                        "allocation": variant, "entrants": n, "basis": "marginal_analytical_distribution"}
                cumulative_population = Fraction(0)
                cumulative_tickets = Fraction(0)
                mean = sum(t*p for t, p in pmf.items())
                concentration.append({**base, **exact_fields("cumulative_population_share", 0), **exact_fields("cumulative_ticket_share", 0)})
                for ticket, p in sorted(pmf.items()):
                    distributions.append({**base, "tickets": ticket, "reachable_in_baseline": p > 0,
                                          "probability_numerator": p.numerator, "probability_denominator": p.denominator,
                                          **exact_fields("probability", p), **exact_fields("expected_entries", n*p),
                                          **exact_fields("expected_total_ticket_contribution", n*ticket*p)})
                    if p:
                        cumulative_population += p
                        cumulative_tickets += ticket*p
                        concentration.append({**base, **exact_fields("cumulative_population_share", cumulative_population),
                                              **exact_fields("cumulative_ticket_share", cumulative_tickets/mean)})
    paths = [{"day1_wins": p.day1_wins, "day1_match_points": p.day1_points, "qualified_day2": p.qualifies,
              "day2_wins": p.day2_wins if p.qualifies else "", "final_match_points": p.final_points,
              "tickets": p.tickets, "scheduled_rounds": p.scheduled_rounds,
              **exact_fields("probability", p.probability)} for p in vegas_paths(rules)]
    stages = []
    for wins, p in binomial_probabilities(6).items():
        stages.append({"stage": "day1_wins", "value": wins, "conditioning": "entrant", **exact_fields("probability", p)})
    q = vegas_metrics(1, rules)["qualification_probability"]
    for label, p in (("qualified", q), ("not_qualified", 1-q)):
        stages.append({"stage": "day2_qualification", "value": label, "conditioning": "entrant", **exact_fields("probability", p)})
    stages.append({"stage": "day2_wins", "value": "not_played", "conditioning": "entrant", **exact_fields("probability", 1-q)})
    for wins, p in binomial_probabilities(5).items():
        stages.extend([{"stage": "day2_wins", "value": wins, "conditioning": "qualified", **exact_fields("probability", p)},
                       {"stage": "day2_wins", "value": wins, "conditioning": "entrant", **exact_fields("probability", q*p)}])
    for points, p in vegas_final_point_distribution(rules).items():
        stages.append({"stage": "final_match_points", "value": points, "conditioning": "entrant", **exact_fields("probability", p)})
    thresholds = []
    for low, high, award in SATURDAY_TIERS:
        thresholds.append({"model": "historical", "allocation": "official_placement", "criterion": "final_placement_inclusive",
                           "low": low, "high": high, "tickets": award, "reachable_no_draw": True,
                           "no_draw_wins_in_band": "", "condition": "final_cut_placement_not_swiss_seed"})
    for low, high, award in sorted(rules.point_tiers):
        wins = [p//3 for p in range(low, high+1) if p % 3 == 0]
        thresholds.append({"model": "vegas", "allocation": "official_match_points", "criterion": "final_match_points_inclusive",
                           "low": low, "high": high, "tickets": award, "reachable_no_draw": bool(wins),
                           "no_draw_wins_in_band": ";".join(map(str, wins)), "condition": "day1_qualification_required_before_sunday"})
    thresholds.append({"model": "vegas", "allocation": "official_match_points", "criterion": "final_match_points_inclusive",
                       "low": 0, "high": 18, "tickets": 0, "reachable_no_draw": True,
                       "no_draw_wins_in_band": "0;1;2;3;4;5;6", "condition": "qualification_alone_does_not_guarantee_tickets"})
    tables = dict(zip(TABLE_NAMES, (comparisons, distributions, paths, stages, thresholds, concentration)))
    metadata = {"model": "exact_fraction_equal_skill_marginal_no_draw_no_bye_no_drop", "vegas_rounds": rules.total_rounds,
                "historical_observed_fields": {r["event_key"]: int(r["observed_n"]) for r in historical},
                "historical_capacity_exception": "Barcelona observed 518 entries exceeds archived advertised cap 512; retained as source exception.",
                "stale_source_round_references": archived["obsolete_award_round_references"],
                "announcement_verification": archived["announcement_verification"],
                "source_records": old_sources + [archived["source"], archived["announcement_source"]],
                "qualification_probability_exact": str(q), "vegas_expected_tickets_per_entrant_exact": str(vegas_metrics(1, rules)["expected_tickets_per_entrant"]),
                "vegas_at_least_40_probability_exact": str(vegas_metrics(1, rules)["at_least_40_probability"]),
                "historical_40_probability_formula": "32/N", "historical_expected_tickets_formula": "4992/N",
                "historical_top8_pool_share_exact": str(Fraction(1728,4992)),
                "comparison_rows": len(comparisons), "scenario_count": len(scenarios(historical)),
                "concentration_scope": "Vegas marginal PMF Gini/Lorenz; not expected realized field Gini or joint finishing distribution."}
    return tables, metadata


def preserved_artifacts_check(root: Path) -> dict:
    manifest = json.loads((root / "data/phase3a/preserved_artifacts.json").read_text())
    differences = [name for name, digest in manifest["files"].items() if not (root/name).is_file() or sha256(root/name) != digest]
    return {"checked_files": len(manifest["files"]), "changed_files": differences, "passed": not differences}


def build(root: Path) -> dict:
    root = Path(root).resolve()
    tables, report = analytical_tables(root)
    for name, rows in tables.items():
        write_csv(root / "outputs/tables" / name, rows)
    write_csv(root / "data/phase3a/sources.csv", report.pop("source_records"))
    inputs = ["outputs/tables/historical_ticket_economy.csv", "data/raw/retrievals.jsonl", "data/raw/phase3a/retrievals.jsonl",
              "data/phase3a/preserved_artifacts.json", "data/phase3a/vegas_rules.json", "data/phase3a/sources.csv"]
    report["input_sha256"] = {p: sha256(root/p) for p in inputs}
    report["code_sha256"] = {p: sha256(root/p) for p in NEW_CODE}
    report["output_sha256"] = {"outputs/tables/"+p: sha256(root/"outputs/tables"/p) for p in TABLE_NAMES}
    write_json(root / "outputs/tables/saturday_analytical_report.json", report)
    return report


def audit(root: Path, *, write: bool = True) -> dict:
    root = Path(root).resolve()
    report = json.loads((root / "outputs/tables/saturday_analytical_report.json").read_text())
    hashes = {**report["input_sha256"], **report["code_sha256"], **report["output_sha256"]}
    mismatches = [p for p, digest in hashes.items() if not (root/p).is_file() or sha256(root/p) != digest]
    expected, current_metadata = analytical_tables(root)
    table_differences = []
    for name, rows in expected.items():
        fields = list(dict.fromkeys(k for r in rows for k in r))
        normalized = [{k: str(r.get(k, "")) for k in fields} for r in rows]
        if read_csv(root/"outputs/tables"/name) != normalized:
            table_differences.append(name)
    source_store = Phase3ASourceStore(root)
    source_records = [json.loads(line) for line in source_store.ledger.read_text().splitlines()]
    for record in source_records:
        source_store.read(record)
    figure_manifest = root / "outputs/figures/saturday_analytical_manifest.json"
    figure_mismatches = []
    if not figure_manifest.is_file():
        figure_mismatches.append(str(figure_manifest.relative_to(root)))
    else:
        figures = json.loads(figure_manifest.read_text())
        figure_hashes = {**figures["input_sha256"], **figures["figure_sha256"],
                         "src/riftbound_tickets/charts/saturday_analytical.py": figures["renderer_sha256"]}
        figure_mismatches.extend(p for p, digest in figure_hashes.items() if not (root/p).is_file() or sha256(root/p) != digest)
    protected = preserved_artifacts_check(root)
    result = {"passed": not mismatches and not table_differences and not figure_mismatches and protected["passed"],
              "source_objects_verified": len(source_records), "hashed_files_checked": len(hashes),
              "hash_mismatches": mismatches, "table_differences": table_differences,
              "figure_hash_mismatches": figure_mismatches,
              "historical_preservation": protected, "independent_recalculation": True,
              "comparison_rows": current_metadata["comparison_rows"]}
    if write:
        write_json(root / "outputs/tables/saturday_analytical_validation.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("collect", "build", "audit", "figures"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--refresh", action="store_true", help="Collect only: append fresh public snapshots")
    args = parser.parse_args()
    if args.command == "collect":
        result = collect_sources(args.root, refresh=args.refresh)
        print(json.dumps({"official_source": result["official_schedule"]["source_id"], "rules": result["rules"]["total_rounds"]}))
    elif args.command == "build":
        result = build(args.root)
        print(json.dumps({"comparison_rows": result["comparison_rows"], "scenario_count": result["scenario_count"]}))
    elif args.command == "figures":
        from .charts.saturday_analytical import render_figures
        print(json.dumps(render_figures(args.root)))
    else:
        result = audit(args.root)
        print(json.dumps(result, indent=2))
        if not result["passed"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
