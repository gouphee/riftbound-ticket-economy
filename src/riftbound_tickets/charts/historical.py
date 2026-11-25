"""Render initial Phase 2 figures from the additive CSVs, never live data."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

FORMATS = ("friday", "saturday", "sunday")
COLORS = {"friday": "#236B8E", "saturday": "#AB5C25", "sunday": "#5D6E42"}


def _read(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def render_historical_figures(root: Path) -> list[str]:
    root = Path(root).resolve()
    os.environ.setdefault("MPLCONFIGDIR", str(root / ".cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter, StrMethodFormatter

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.titlesize": 13, "axes.titleweight": "bold",
                         "figure.facecolor": "#FBFAF7", "axes.facecolor": "#FBFAF7", "svg.hashsalt": "riftbound-historical-phase2"})
    tables = root / "outputs/tables"
    summary = _read(tables / "historical_ticket_economy.csv")
    rates = _read(tables / "historical_draw_rates.csv")
    distributions = _read(tables / "historical_award_distribution.csv")
    cities = [r["city"] for r in summary if r["event_format"] == "friday"]
    output = root / "outputs/figures"
    output.mkdir(parents=True, exist_ok=True)
    files = []

    def save(fig, name, footer):
        fig.text(.065, .025, footer, ha="left", va="bottom", fontsize=8, color="#505050")
        for suffix in ("svg", "png"):
            path = output / (name + "." + suffix)
            metadata = {"Date": None} if suffix == "svg" else {"Software": "Matplotlib " + matplotlib.__version__}
            fig.savefig(path, dpi=180, metadata=metadata)
            files.append(str(path.relative_to(root)))
        plt.close(fig)

    for format_ in ("friday", "sunday"):
        rows = [r for r in summary if r["event_format"] == format_]
        fig, ax = plt.subplots(figsize=(11.5, 6.2))
        x = list(range(len(rows)))
        observed = [int(r["observed_standings_implied_tickets"]) for r in rows]
        ceilings = [int(r["theoretical_upper_bound_tickets"]) for r in rows]
        constructed = [int(r["no_draw_swiss_constructed_tickets"]) for r in rows]
        ax.bar([i - .19 for i in x], observed, width=.35, color=COLORS[format_], label="Observed final-record tickets (includes drops)")
        ax.bar([i + .19 for i in x], ceilings, width=.35, color="#DFDFD9", edgecolor="#88887E", hatch="///", linewidth=.5,
               label="Proved ceiling; Swiss/opponent constraints relaxed")
        ax.scatter([i + .19 for i in x], constructed, color="#B38324", marker="D", s=36, edgecolors="#FBFAF7", linewidths=.7, zorder=4,
                   label="One feasible no-draw Swiss construction; not optimized")
        for i, value in enumerate(observed):
            ax.text(i - .19, value + max(ceilings) * .018, f"{value:,}", ha="center", fontsize=8, color=COLORS[format_])
        ax.set_xticks(x, cities)
        ax.set_ylabel("Prize-wall tickets")
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.set_title(f"{format_.title()}: observed tickets versus a proved ceiling", loc="left", pad=55)
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), frameon=False, fontsize=8.5)
        ax.set_ylim(0, max(ceilings) * 1.13)
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
        fig.subplots_adjust(left=.08, right=.98, bottom=.15, top=.76)
        save(fig, "historical_" + format_ + "_observed_vs_bound",
             "N = final standings entries, including zero-match rows. Full participation; no draws in the reference.\n"
             "The exact Swiss maximum is unresolved. Differences are not an estimate of tickets lost specifically to draws.")

    fig, axes = plt.subplots(1, 3, figsize=(13, 5.8), sharey=True)
    common_per_entry_limit = max(float(r["tickets_per_standings_entry"]) for r in summary) * 1.2
    for ax, format_ in zip(axes, FORMATS):
        rows = [r for r in summary if r["event_format"] == format_]
        values = [float(r["tickets_per_standings_entry"]) for r in rows]
        ax.barh(list(range(8)), values, color=COLORS[format_], alpha=.9)
        ax.set_yticks(list(range(8)), cities)
        ax.invert_yaxis()
        ax.set_title(format_.title() + (" (conditional)" if format_ == "saturday" else ""), loc="left")
        ax.set_xlabel("Tickets per standings entry")
        ax.set_xlim(0, common_per_entry_limit)
        for i, value in enumerate(values):
            ax.text(value + max(values) * .025, i, f"{value:.2f}", va="center", fontsize=9)
        ax.grid(axis="x", alpha=.15)
        ax.set_axisbelow(True)
    fig.suptitle("Ticket availability per recorded field entry", x=.12, ha="left", fontsize=16, fontweight="bold")
    fig.subplots_adjust(left=.12, right=.98, bottom=.17, top=.84, wspace=.17)
    save(fig, "historical_tickets_per_entry", "Friday/Sunday: all recorded qualifying results. Saturday: all Top 128 slots assumed funded.\n"
         "These are event entries, not distinct weekend attendees or confirmed physical ticket claims.")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.6))
    saturday = [r for r in summary if r["event_format"] == "saturday"]
    axes[0].barh(list(range(8)), [4992] * 8, color=COLORS["saturday"])
    axes[0].set_yticks(list(range(8)), cities)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, 6200)
    axes[0].set_xlabel("Conditional published tickets")
    axes[0].set_title("The same 4,992-ticket pool", loc="left")
    for i in range(8):
        axes[0].text(5050, i, "4,992", va="center", fontsize=9)
    values = [float(r["tickets_per_standings_entry"]) for r in saturday]
    axes[1].barh(list(range(8)), values, color="#BF9876")
    axes[1].set_yticks(list(range(8)), [f"N = {r['observed_n']}" for r in saturday])
    axes[1].invert_yaxis()
    axes[1].set_xlim(0, 46)
    axes[1].set_title("Different field sizes", loc="left")
    axes[1].set_xlabel("Conditional tickets per standings entry")
    for i, value in enumerate(values):
        axes[1].text(value + .5, i, f"{value:.2f}", va="center", fontsize=9)
    fig.suptitle("Saturday's fixed Top 128 schedule pool", x=.12, ha="left", fontsize=16, fontweight="bold")
    fig.subplots_adjust(left=.12, right=.98, bottom=.18, top=.83, wspace=.34)
    save(fig, "historical_saturday_fixed_pool", "All 128 advertised places assumed awarded: 8 events x 4,992 = 39,936 tickets.\n"
         "Unfinished cuts affect individual allocation; the 216-each Top 8 split conserves the 1,728-ticket Top 8 pool.")

    fig, axes = plt.subplots(3, 1, figsize=(11.5, 11))
    for ax, format_ in zip(axes, FORMATS):
        basis = "conditional_official_rank_slots_not_player_finish_claims" if format_ == "saturday" else "observed_standings_implied"
        dist = [r for r in distributions if r["event_format"] == format_ and r["basis"] == basis]
        tickets = sorted({int(r["tickets_per_entry"]) for r in dist if r["tickets_per_entry"]})
        matrix = [[sum(float(r["share_of_standings_entries"]) for r in dist if r["city"] == city and r["tickets_per_entry"] == str(ticket)) for ticket in tickets] for city in cities]
        im = ax.imshow(matrix, vmin=0, vmax=.75, cmap="Blues", aspect="auto")
        ax.set_xticks(list(range(len(tickets))), tickets)
        ax.set_yticks(list(range(8)), cities)
        ax.set_title(format_.title() + (": conditional official rank-slot allocation" if format_ == "saturday" else ": recorded individual awards"), loc="left")
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                ax.text(j, i, f"{100 * value:.1f}%" if value else "-", ha="center", va="center", fontsize=7.7,
                        color="white" if value > .44 else "#222222")
        ax.set_xlabel("Ticket award")
    fig.subplots_adjust(left=.12, right=.88, bottom=.1, top=.94, hspace=.64)
    cax = fig.add_axes([.91, .3, .018, .4])
    fig.colorbar(im, cax=cax, format=PercentFormatter(1), label="Share of standings entries")
    save(fig, "historical_individual_award_distribution", "Saturday cells are funded rank slots, not claims about unidentified Top 8 finishes.\n"
         "The separate CSV also retains the 216-each split scenario and unresolved archived individual payouts.")

    fig, axes = plt.subplots(2, 1, figsize=(12, 8.4))
    for offset, format_ in zip((-.25, 0, .25), FORMATS):
        rows = {r["event_key"]: r for r in rates if r["group_type"] == "event" and r["event_format"] == format_}
        rows = [rows[r["event_key"]] for r in summary if r["event_format"] == format_]
        y = [float(r["draw_rate"]) for r in rows]
        error = [[v - float(r["draw_rate_wilson95_low"]) for v, r in zip(y, rows)],
                 [float(r["draw_rate_wilson95_high"]) - v for v, r in zip(y, rows)]]
        axes[0].bar([i + offset for i in range(8)], y, width=.23, label=format_.title(), color=COLORS[format_], yerr=error,
                    error_kw={"elinewidth":.8,"capsize":2})
        rounds = sorted([r for r in rates if r["group_type"] == "event_format_round" and r["event_format"] == format_ and r["draw_rate"]], key=lambda r: int(r["round_number"]))
        axes[1].plot([int(r["round_number"]) for r in rounds], [float(r["draw_rate"]) for r in rounds],
                     color=COLORS[format_], marker="o", label=format_.title())
    axes[0].set_xticks(list(range(8)), cities)
    axes[0].set_title("By event: unique completed played Swiss matches", loc="left")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=3, loc="upper right", bbox_to_anchor=(.98, .98))
    axes[1].set_title("By Swiss round: match-weighted across cities", loc="left")
    axes[1].set_xlabel("Swiss round")
    axes[1].set_xticks(range(1,8))
    for ax in axes:
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.set_ylabel("Explicit match draw rate")
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
    fig.suptitle("Observed Swiss draw rates", x=.085, ha="left", fontsize=17, fontweight="bold")
    fig.subplots_adjust(left=.085, right=.98, bottom=.14, top=.88, hspace=.44)
    save(fig, "historical_draw_rates", "1,150 explicit draws / 50,262 played matches = 2.29%; excludes 130 byes and 234 one-player loss non-games.\n"
         "Friday Round 6 has played matches from Atlanta only; Singapore's empty Round 6 contributes no denominator.\n"
         "Error bars: descriptive 95% Wilson intervals (independent-match assumption; not cluster adjusted). No causal format claim.")
    inputs = [tables / name for name in ("historical_ticket_economy.csv", "historical_draw_rates.csv", "historical_award_distribution.csv")]
    manifest = {"renderer": "matplotlib", "version": matplotlib.__version__, "figures": files,
                "input_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
    (tables / "historical_figure_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return files
