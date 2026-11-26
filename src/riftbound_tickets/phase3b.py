"""Offline Phase 3B draw sensitivity and local outcome tables.

Uses the preserved Phase 3A official sources and leaves previous exports intact.
Run ``python -m riftbound_tickets.phase3b build|audit|figures``.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from .models.saturday_analytical import (
    vegas_final_point_distribution, vegas_metrics, vegas_ticket_distribution,
)
from .models.saturday_draws import (
    DRAW_RATES, equal_skill_outcomes, feasible_no_prior_draw_scores,
    match_point_distribution, outcome_matrix, vegas_draw_final_points,
    vegas_draw_metrics, vegas_draw_paths, vegas_draw_ticket_distribution,
)
from .phase3a import exact_fields, historical_inputs, read_csv, rules_from_archive, sha256, write_csv, write_json

NEW_CODE = (
    "src/riftbound_tickets/models/saturday_draws.py",
    "src/riftbound_tickets/phase3b.py",
    "src/riftbound_tickets/charts/saturday_draws.py",
    "scripts/validate_phase3b.py",
    "tests/test_saturday_draws.py",
    "tests/test_phase3b_outputs.py",
)
TABLE_NAMES = (
    "saturday_draw_sensitivity.csv", "saturday_draw_ticket_distributions.csv",
    "saturday_draw_final_points.csv", "saturday_final_round_outcomes.csv",
    "saturday_draw_historical_comparison.csv", "saturday_draw_point_paths.csv",
    "saturday_draw_stage_points.csv",
)


def scenario_fields(rate: Fraction) -> dict:
    probabilities = equal_skill_outcomes(rate)
    return {"draw_scenario": f"draw-{int(rate*100)}pct", **exact_fields("draw_rate", rate),
            **exact_fields("win_probability", probabilities.win), **exact_fields("loss_probability", probabilities.loss)}


def _serialize_exact(row: dict) -> dict:
    result = {}
    for key, value in row.items():
        if isinstance(value,Fraction):
            result.update(exact_fields(key,value))
        else:
            result[key] = value
    return result


def analytical_tables(root: Path) -> tuple[dict[str,list[dict]], dict, dict]:
    archived,rules = rules_from_archive(root)
    historical,old_sources = historical_inputs(root)
    prior_comparisons = read_csv(root/"outputs/tables/saturday_analytical_comparison.csv")
    if len(prior_comparisons) != 24:
        raise ValueError("Phase 3A comparison input is incomplete")
    sensitivity,distributions,points,outcomes,comparisons,paths,stages = [],[],[],[],[],[],[]
    source_fields = {"vegas_rule_source_id":archived["source"]["source_id"],"vegas_rule_source_url":archived["source"]["url"]}
    metric_cache = {}
    for rate in DRAW_RATES:
        probabilities = equal_skill_outcomes(rate)
        base = {**scenario_fields(rate),**source_fields,"basis":"exact_marginal_independent_wdl_not_physical_issuance"}
        metric_cache[rate] = vegas_draw_metrics(1,rules,probabilities)
        for n in (512,1024):
            row = {**base,"entrants":n,"attendance_basis":"hypothetical_within_vegas_cap_not_observed_attendance",
                   "vegas_published_capacity":archived["published_capacity"],"vegas_total_basis":"expected_total_not_maximum"}
            for name,value in vegas_draw_metrics(n,rules,probabilities).items():
                row.update(exact_fields(name,value))
            sensitivity.append(row)
        pmf = vegas_draw_ticket_distribution(rules,probabilities)
        for award,mass in pmf.items():
            row = {**base,"tickets":award,"reachable_in_scenario":mass>0,"probability_numerator":mass.numerator,
                   "probability_denominator":mass.denominator,**exact_fields("probability",mass)}
            for n in (512,1024):
                row.update(exact_fields(f"expected_entries_{n}",n*mass))
                row.update(exact_fields(f"expected_ticket_contribution_{n}",n*award*mass))
            distributions.append(row)
        for point,mass in vegas_draw_final_points(rules,probabilities).items():
            points.append({**base,"final_match_points":point,**exact_fields("probability",mass)})
        for path in vegas_draw_paths(rules,probabilities):
            paths.append({**base,"day1_points":path.day1_points,"qualified_day2":path.qualifies,
                          "day2_points":path.day2_points if path.qualifies else "", "final_points":path.final_points,
                          "tickets":path.tickets,"rounds_played":path.rounds_played,**exact_fields("probability",path.probability)})
        q = metric_cache[rate]["qualification_probability"]
        for point,mass in match_point_distribution(6,probabilities).items():
            stages.append({**base,"stage":"day1_points","conditioning":"entrant","points":point,**exact_fields("probability",mass)})
        stages.append({**base,"stage":"day2_points","conditioning":"entrant","points":"not_played",**exact_fields("probability",1-q)})
        for point,mass in match_point_distribution(5,probabilities).items():
            stages.append({**base,"stage":"day2_points","conditioning":"qualified","points":point,**exact_fields("probability",mass)})
            stages.append({**base,"stage":"day2_points","conditioning":"entrant","points":point,**exact_fields("probability",q*mass)})
        # Preserve every original attendance label and historical allocation.
        for prior in prior_comparisons:
            row = {**base,**{k:v for k,v in prior.items() if k.startswith("historical_") or k in (
                "scenario_id","scenario_kind","vegas_n","vegas_attendance_status","observed_historical_event_key","vegas_published_capacity")},
                "historical_total_basis":"fixed_funded_4992_pool", "vegas_total_basis":"expected_total_not_maximum"}
            for name,value in vegas_draw_metrics(int(prior["vegas_n"]),rules,probabilities).items():
                row.update(exact_fields("vegas_"+name,value))
            comparisons.append(row)
    for round_number in (11,6):
        scores = feasible_no_prior_draw_scores(round_number,rules)
        future_rates = (None,) if round_number==11 else DRAW_RATES
        for rate in future_rates:
            for a in scores:
                for b in scores:
                    rows = outcome_matrix(round_number,a,b,rules,equal_skill_outcomes(rate) if rate is not None else None)
                    for row in rows:
                        outcomes.append({**source_fields,
                                         "future_draw_scenario":scenario_fields(rate)["draw_scenario"] if rate is not None else "not_applicable_terminal_round",
                                         "future_draw_rate_exact":str(rate) if rate is not None else "",
                                         **_serialize_exact(row)})
    zero = metric_cache[Fraction(0)]
    zero_equal = (vegas_draw_ticket_distribution(rules,equal_skill_outcomes(Fraction(0))) == vegas_ticket_distribution(rules)
                  and vegas_draw_final_points(rules,equal_skill_outcomes(Fraction(0))) == vegas_final_point_distribution(rules)
                  and all(zero[k] == value for k,value in vegas_metrics(1,rules).items()))
    if not zero_equal:
        raise ValueError("Draw-free extension differs from preserved Phase 3A baseline")
    tables = dict(zip(TABLE_NAMES,(sensitivity,distributions,points,outcomes,comparisons,paths,stages)))
    terminal = [r for r in outcomes if r["round"]==11 and r["outcome"]=="draw" and r["a_start_points"]<=r["b_start_points"]]
    metadata = {"model":"exact_fraction_gated_points_generating_function_independent_marginal_wdl",
                "vegas_rounds":11,"qualification_cut_match_points":12,
                "draw_rates_exact":[str(d) for d in DRAW_RATES],"zero_draw_reproduces_phase3a":zero_equal,
                "historical_recorded_field_sizes":{r["event_key"]:int(r["observed_n"]) for r in historical},
                "round11_equal_score_cases":sum(r["equal_start_points"] for r in terminal),
                "round11_equal_score_cases_same_combined_tickets":sum(r["equal_start_points"] and r["all_outcomes_equal_combined_tickets"] for r in terminal),
                "round11_unequal_unordered_pairs":sum(not r["equal_start_points"] for r in terminal),
                "round11_unequal_pairs_with_differing_totals":sum(not r["equal_start_points"] and not r["all_outcomes_equal_combined_tickets"] for r in terminal),
                "round11_draw_equals_fair_decisive_expected_combined_tickets":all(
                    r["draw_minus_a_win_combined_tickets"]+r["draw_minus_b_win_combined_tickets"]==0 for r in terminal),
                "matrix_scope":"Individually feasible no-prior-draw records; conditional pairwise identities. Joint Swiss pairing feasibility and frequencies are not established.",
                "round6_future_ev_scope":"Conditional on forced local outcome and specified independent Sunday draw rate; qualification is not a guaranteed award.",
                "table_rows":{name:len(rows) for name,rows in tables.items()}}
    review = {"review_date":"2026-11-25","review_basis":"Existing immutable archived official sources; no live refresh in Phase 3B",
              "source_records":old_sources+[archived["source"],archived["announcement_source"]],
              "vegas_point_tiers":[list(t) for t in rules.point_tiers],"day1_rounds":6,"day2_rounds":5,
              "day2_cut_match_points":12,"scoring":{"win":3,"draw":1,"loss":0},
              "obsolete_schedule_award_round_references":archived["obsolete_award_round_references"],
              "round_resolution":archived["round_resolution"],"announcement_verification":archived["announcement_verification"]}
    return tables,metadata,review


def preservation_check(root: Path) -> dict:
    manifest = json.loads((root/"data/phase3b/preserved_artifacts.json").read_text())
    changed = [name for name,digest in manifest["files"].items() if not (root/name).is_file() or sha256(root/name)!=digest]
    return {"checked_files":len(manifest["files"]),"changed_files":changed,"passed":not changed}


def build(root: Path) -> dict:
    root = Path(root).resolve()
    tables,report,review = analytical_tables(root)
    for name,rows in tables.items():
        write_csv(root/"outputs/tables"/name,rows)
    write_json(root/"data/phase3b/source_review.json",review)
    inputs = ("data/phase3b/preserved_artifacts.json","data/phase3b/source_review.json",
              "data/raw/retrievals.jsonl","data/raw/phase3a/retrievals.jsonl","data/phase3a/vegas_rules.json",
              "data/phase3a/sources.csv","outputs/tables/historical_ticket_economy.csv",
              "outputs/tables/saturday_analytical_comparison.csv","outputs/tables/saturday_ticket_distributions.csv")
    report["input_sha256"] = {p:sha256(root/p) for p in inputs}
    report["code_sha256"] = {p:sha256(root/p) for p in NEW_CODE}
    report["output_sha256"] = {"outputs/tables/"+p:sha256(root/"outputs/tables"/p) for p in TABLE_NAMES}
    write_json(root/"outputs/tables/saturday_draw_report.json",report)
    return report


def audit(root: Path, *, write: bool = True) -> dict:
    root = Path(root).resolve()
    report = json.loads((root/"outputs/tables/saturday_draw_report.json").read_text())
    hashes = {**report["input_sha256"],**report["code_sha256"],**report["output_sha256"]}
    mismatches = [p for p,d in hashes.items() if not (root/p).is_file() or sha256(root/p)!=d]
    tables,metadata,review = analytical_tables(root)
    differences = []
    for name,rows in tables.items():
        fields = list(dict.fromkeys(key for row in rows for key in row))
        expected = [{k:str(r.get(k,"")) for k in fields} for r in rows]
        if read_csv(root/"outputs/tables"/name)!=expected:
            differences.append(name)
    if json.loads((root/"data/phase3b/source_review.json").read_text()) != review:
        differences.append("data/phase3b/source_review.json")
    figure_manifest = root/"outputs/figures/saturday_draw_manifest.json"
    figure_mismatches = []
    if not figure_manifest.exists():
        figure_mismatches.append(str(figure_manifest.relative_to(root)))
    else:
        figures = json.loads(figure_manifest.read_text())
        figure_hashes = {**figures["input_sha256"],**figures["figure_sha256"],
                         "src/riftbound_tickets/charts/saturday_draws.py":figures["renderer_sha256"]}
        figure_mismatches = [p for p,d in figure_hashes.items() if not (root/p).is_file() or sha256(root/p)!=d]
    protected = preservation_check(root)
    result = {"passed":not mismatches and not differences and not figure_mismatches and protected["passed"],
              "hash_mismatches":mismatches,"table_differences":differences,"figure_hash_mismatches":figure_mismatches,
              "preservation":protected,"table_recalculation":True,"zero_draw_reproduces_phase3a":metadata["zero_draw_reproduces_phase3a"],
              "official_source_review":"Both Vegas captures and all eight historical payout sources hash-verified and re-parsed by the reused Phase 3A source checks"}
    if write:
        write_json(root/"outputs/tables/saturday_draw_validation.json",result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("build","audit","figures"))
    parser.add_argument("--root",type=Path,default=Path.cwd())
    args = parser.parse_args()
    if args.command=="build":
        report = build(args.root)
        print(json.dumps(report["table_rows"],indent=2))
    elif args.command=="figures":
        from .charts.saturday_draws import render_figures
        print(json.dumps(render_figures(args.root)))
    else:
        result = audit(args.root)
        print(json.dumps(result,indent=2))
        if not result["passed"]:
            raise SystemExit(1)


if __name__=="__main__":
    main()
