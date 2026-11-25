"""Publication figures from exact Phase 3A CSV exports; optional Matplotlib."""

from __future__ import annotations

import os
from pathlib import Path

from ..phase3a import TABLE_NAMES, read_csv, sha256, write_json


def render_figures(root: Path) -> list[str]:
    root = Path(root).resolve()
    os.environ.setdefault("MPLCONFIGDIR", str(root / ".cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter, StrMethodFormatter

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlesize": 13, "axes.titleweight": "bold",
                         "figure.facecolor": "#FBFAF7", "axes.facecolor": "#FBFAF7",
                         "svg.hashsalt": "riftbound-saturday-phase3a"})
    old, new, split_color = "#A45925", "#216B8D", "#75814C"
    tables, output = root / "outputs/tables", root / "outputs/figures"
    output.mkdir(parents=True, exist_ok=True)
    comparisons = read_csv(tables / TABLE_NAMES[0])
    baseline = next(r for r in comparisons if r["scenario_id"] == "equal-512" and r["historical_allocation"] == "official_placement")
    observed = [r for r in comparisons if r["scenario_kind"].startswith("observed_") and r["historical_allocation"] == "official_placement"]
    p40 = float(baseline["vegas_at_least_40_probability"])
    ev = float(baseline["vegas_expected_tickets_per_entrant"])
    files = []

    def save(fig, name, footer):
        fig.text(.075, .025, footer, ha="left", va="bottom", fontsize=8, color="#505050")
        for extension in ("svg", "png"):
            path = output / f"saturday_analytical_{name}.{extension}"
            metadata = {"Date": None} if extension == "svg" else {"Software": "Matplotlib " + matplotlib.__version__}
            fig.savefig(path, dpi=200, metadata=metadata)
            files.append(str(path.relative_to(root)))
        plt.close(fig)

    def attendance_axis(ax):
        ax.axvspan(512, 1024, color="#E5E2DA", alpha=.55, zorder=0)
        ax.axvline(512, color="#8A867D", lw=.9, ls=":")
        ax.set_xlim(128, 1024)
        ax.set_xticks([128, 256, 512, 768, 1024])
        ax.set_xlabel("Entrants (scenario; Vegas attendance unknown)")
        ax.grid(axis="y", alpha=.18)

    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    attendance_axis(ax)
    ax.plot(range(128, 513), [32/n for n in range(128, 513)], color=old, lw=2.5, label="Historical: 32 funded slots / N")
    ax.plot(range(512, 1025), [32/n for n in range(512, 1025)], color=old, lw=2, ls="--", label="Historical extension beyond published cap")
    ax.axhline(p40, color=new, lw=2.5, label=f"Vegas: {100*p40:.4f}% (all N in marginal model)")
    ax.scatter([int(r["historical_n"]) for r in observed], [float(r["historical_at_least_40_probability"]) for r in observed],
               s=32, color=old, edgecolors="#FBFAF7", zorder=5, label="Eight observed historical field sizes")
    ax.scatter([518], [32/518], facecolors="none", edgecolors="#813B73", s=120, zorder=6)
    ax.annotate("Barcelona: observed 518\nexceeds advertised cap 512", (518, 32/518), (660, .10),
                fontsize=8.5, color="#813B73", arrowprops={"arrowstyle": "-", "color": "#813B73"})
    ax.annotate("N = 512: 6.25%", (512, .0625), (290, .10), fontsize=10, color=old,
                arrowprops={"arrowstyle": "-", "color": old})
    ax.set_ylim(0, .27)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylabel("Probability of earning at least 40 tickets")
    ax.set_title("At the old 512-player cap, the 40-ticket chance nearly halves", loc="left", pad=84)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), frameon=False, fontsize=8.5)
    fig.subplots_adjust(left=.09, right=.97, bottom=.18, top=.70)
    save(fig, "chance_40", "Analytical equal-skill benchmark: no draws, byes or drops; Vegas applies the Day 2 gate before Sunday.\n"
         "Shading: historical attendance beyond advertised 512 cap. Tickets do not guarantee physical Metal Legend redemption.")

    distributions = [r for r in read_csv(tables / TABLE_NAMES[1]) if r["scenario_id"] == "equal-512" and r["allocation"] != "reported_216_each_top8_scenario"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.3), gridspec_kw={"width_ratios": [1, 3.6]})
    labels = [("historical", "Historical", old), ("vegas", "Vegas", new)]
    for index, (model, label, color) in enumerate(labels):
        zero = float(next(r["probability"] for r in distributions if r["model"] == model and r["tickets"] == "0"))
        axes[0].bar(index, zero, color=color, width=.65)
        axes[0].text(index, zero+.025, f"{zero:.2%}", ha="center", color=color)
    axes[0].set_xticks([0, 1], ["Historical", "Vegas"])
    axes[0].set_ylim(0, 1)
    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[0].set_title("Zero tickets", loc="left")
    awards = sorted({int(r["tickets"]) for r in distributions if int(r["tickets"]) > 0 and float(r["probability"]) > 0})
    for offset, (model, label, color) in zip((-.19,.19), labels):
        lookup = {int(r["tickets"]): float(r["probability"]) for r in distributions if r["model"] == model}
        for i, award in enumerate(awards):
            p = lookup.get(award, 0)
            if p:
                axes[1].bar(i+offset, p, width=.35, color=color, label=label if award == (18 if model == "historical" else 20) else None)
    axes[1].set_xticks(range(len(awards)), awards)
    axes[1].set_yscale("log")
    axes[1].set_ylim(.0002, .3)
    axes[1].set_yticks([.0005,.001,.01,.1], ["0.05%","0.1%","1%","10%"])
    axes[1].set_xlabel("Individual ticket award")
    axes[1].set_ylabel("Probability (log scale)")
    axes[1].set_title("Every reachable positive award at N = 512", loc="left")
    axes[1].legend(frameon=False)
    for ax in axes:
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
    fig.suptitle("The Vegas distribution has a lower ceiling and more zero-ticket outcomes", x=.075, y=.96, ha="left", fontsize=15, fontweight="bold")
    fig.subplots_adjust(left=.075, right=.98, bottom=.20, top=.82, wspace=.30)
    save(fig, "ticket_distribution", "Analytical equal-skill, no-draw benchmark. Historical official placements; all 128 awards funded.\n"
         "Published Vegas awards of 10, 25, 35, 50 and 70 tickets have probability zero here; retained in the CSV.")

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.2))
    for ax in axes:
        attendance_axis(ax)
    for low, high, style in ((128,512,"-"),(512,1024,"--")):
        ns = list(range(low, high+1))
        axes[0].plot(ns, [4992/n for n in ns], color=old, lw=2.4, ls=style, label="Historical: 4,992 / N" if low==128 else None)
        axes[1].plot(ns, [4992]*len(ns), color=old, lw=2.4, ls=style, label="Historical: fixed 4,992" if low==128 else None)
    axes[0].axhline(ev, color=new, lw=2.4, label=f"Vegas: {ev:.4f}")
    axes[1].plot([128,1024], [128*ev,1024*ev], color=new, lw=2.4, label="Vegas: N × 5.65918…")
    axes[0].scatter([512],[9.75],color=old,zorder=5)
    axes[0].annotate("512: 9.75 vs 5.66", (512,9.75), (565,18), fontsize=9, arrowprops={"arrowstyle":"-"})
    axes[1].scatter([1024],[1024*ev],color=new,zorder=5)
    axes[1].annotate("Vegas cap 1,024:\n5,795 expected", (1024,1024*ev), (600,6500), fontsize=9, color=new, arrowprops={"arrowstyle":"-","color":new})
    axes[0].set_ylim(0,42)
    axes[1].set_ylim(0,8000)
    axes[0].set_ylabel("Expected tickets per entrant")
    axes[1].set_ylabel("Expected total tickets (not a maximum)")
    axes[1].yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    axes[0].set_title("Per entrant", loc="left")
    axes[1].set_title("Across the field", loc="left")
    for ax in axes:
        ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.suptitle("Less per player at 512; a larger full-cap Vegas event can generate more", x=.075, y=.96, ha="left", fontsize=15, fontweight="bold")
    fig.subplots_adjust(left=.075, right=.98, bottom=.20, top=.82, wspace=.24)
    save(fig, "expected_tickets", "Exact expectations under the equal-skill marginal model; Vegas attendance is a scenario, not a forecast.\n"
         "Shading/dashes: historical extension beyond published cap 512. Historical full cap = 512; Vegas full cap = 1,024.")

    lorenz = [r for r in read_csv(tables / TABLE_NAMES[5]) if r["scenario_id"] == "equal-512"]
    fig, ax = plt.subplots(figsize=(8, 6.5))
    for variant, label, color in (("official_placement","Historical official",old), ("reported_216_each_top8_scenario","Historical 216-each Top 8 scenario",split_color), ("official_match_points","Vegas marginal distribution",new)):
        rows = [r for r in lorenz if r["allocation"] == variant]
        ax.plot([float(r["cumulative_population_share"]) for r in rows], [float(r["cumulative_ticket_share"]) for r in rows], color=color, label=label, lw=2.3)
    ax.plot([0,1],[0,1],color="#B5B2A9",ls=":",label="Equal tickets for every entrant")
    ax.set(xlim=(0,1),ylim=(0,1),xlabel="Cumulative entrant probability, lowest award first",ylabel="Cumulative share of expected tickets")
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.grid(alpha=.15)
    ax.set_title("A lower ceiling also reduces marginal ticket concentration", loc="left", pad=20)
    ax.legend(loc="upper left",frameon=False,fontsize=9)
    fig.subplots_adjust(left=.12,right=.97,bottom=.20,top=.88)
    save(fig, "concentration", "N = 512, analytical equal-skill distributions. Vegas curve describes the marginal award distribution;\n"
         "it is not the expected realized tournament Lorenz curve. The Top 8 split conserves the historical pool.")

    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.axis("off")
    rows = [["Any tickets", "Top 128 → 18+", "21 points / 7 wins → 20+"],
            ["40+ tickets", "Top 32 → 48+", "27 points / 9 wins → 40+"],
            ["80+ tickets", "Top 8 → 144+", "33 points / 11 wins → 80"],
            ["Maximum", "1st → 432", "33 points / 11 wins → 80"],
            ["Advancement gate", "Top 8 cut after 7 Swiss", "12 points / 4 wins after 6 rounds"],
            ["Rounds scheduled", "7 + up to 3 cut rounds", "6; 11 if qualified"]]
    table = ax.table(cellText=rows, colLabels=["Threshold", "Historical official placement", "Vegas no-draw baseline"],
                     cellLoc="left",colLoc="left",loc="center",colWidths=[.23,.34,.43])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1,2.1)
    for (r,c), cell in table.get_celld().items():
        cell.set_edgecolor("#DAD7CD")
        cell.set_facecolor("#F0EDE5" if r==0 else "#FBFAF7")
        if r==0:
            cell.set_text_props(weight="bold")
    ax.set_title("What results guarantee tickets under the published rules?", loc="left",pad=24)
    fig.subplots_adjust(left=.055,right=.98,bottom=.20,top=.85)
    save(fig, "reward_thresholds", "Vegas win counts assume no draws and the Day 2 gate; qualifying alone does not guarantee tickets.\n"
         "Thresholds describe rule entitlements, not physical claims. Historical Top 8 split scenario: 216 each; other tiers unchanged.")
    manifest = {"matplotlib_version": matplotlib.__version__, "renderer_sha256": sha256(Path(__file__)),
                "input_sha256": {"outputs/tables/"+name: sha256(tables/name) for name in TABLE_NAMES},
                "figure_sha256": {name: sha256(root/name) for name in files},
                "scope": "Phase 3A analytical benchmarks only; historical figures untouched"}
    write_json(output / "saturday_analytical_manifest.json", manifest)
    return files
