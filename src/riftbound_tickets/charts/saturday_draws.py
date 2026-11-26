"""Phase 3B standalone figures from audited exact CSVs; no live retrievals."""

from __future__ import annotations

import os
from pathlib import Path

from ..phase3a import read_csv, sha256, write_json
from ..phase3b import TABLE_NAMES


def render_figures(root: Path) -> list[str]:
    root = Path(root).resolve()
    os.environ.setdefault("MPLCONFIGDIR",str(root/".cache/matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import PercentFormatter, StrMethodFormatter

    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
                         "axes.spines.right":False,"axes.titlesize":12,"axes.titleweight":"bold",
                         "figure.facecolor":"#FBFAF7","axes.facecolor":"#FBFAF7","svg.hashsalt":"riftbound-phase3b"})
    old,new,light = "#A45925","#216B8D","#7AA8BA"
    tables,output = root/"outputs/tables",root/"outputs/figures"
    output.mkdir(parents=True,exist_ok=True)
    summary = read_csv(tables/TABLE_NAMES[0])
    main = [r for r in summary if r["entrants"]=="1024"]
    comparison = read_csv(tables/TABLE_NAMES[4])
    h512 = next(r for r in comparison if r["scenario_id"]=="equal-512" and r["historical_allocation"]=="official_placement")
    x = [float(r["draw_rate"])*100 for r in main]
    files = []

    def save(fig,name,footer):
        fig.text(.075,.025,footer,ha="left",va="bottom",fontsize=8,color="#505050")
        for suffix in ("svg","png"):
            path = output/f"saturday_draw_{name}.{suffix}"
            metadata = {"Date":None} if suffix=="svg" else {"Software":"Matplotlib "+matplotlib.__version__}
            fig.savefig(path,dpi=200,metadata=metadata)
            files.append(str(path.relative_to(root)))
        plt.close(fig)

    def draw_axis(ax):
        ax.set_xticks(x,["0%","1%","2%","5%"])
        ax.set_xlabel("Assumed per-match draw probability")
        ax.grid(axis="y",alpha=.18)
        ax.set_axisbelow(True)

    fig,axes = plt.subplots(1,2,figsize=(11.5,6))
    for ax,field,label in zip(axes,("qualification_probability","at_least_40_probability"),("Reach Day 2","Earn at least 40 tickets")):
        values = [float(r[field]) for r in main]
        ax.plot(x,values,color=new,lw=2.4,marker="o",ms=6,label="Vegas equal-skill sensitivity")
        for i,(xx,v) in enumerate(zip(x,values)):
            ax.annotate(f"{v:.3%}",(xx,v),(0,12 if i%2==0 else -19),textcoords="offset points",ha="center",fontsize=9,color=new)
        draw_axis(ax)
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.set_ylabel("Entrant probability")
        ax.set_title(label,loc="left")
    axes[0].set_ylim(.27,.38)
    axes[1].axhline(float(h512["historical_at_least_40_probability"]),color=old,lw=2,ls="--",label="Historical at N=512: 6.25%")
    axes[1].set_ylim(0,.072)
    axes[1].legend(frameon=False,loc="upper right",fontsize=8.5)
    fig.suptitle("More independent draws reduce qualification and the 40-ticket chance",x=.075,y=.97,ha="left",fontsize=15,fontweight="bold")
    fig.subplots_adjust(left=.075,right=.97,bottom=.20,top=.82,wspace=.28)
    save(fig,"probabilities","Exact marginal W/D/L benchmark: wins and losses each have probability (1 − draw rate)/2.\n"
         "Six rounds, 12-point Day 2 gate, then five rounds for qualifiers. Historical Round 7 rates are not imported.")

    fig,axes = plt.subplots(1,2,figsize=(11.8,6.2))
    ev = [float(r["expected_tickets_per_entrant"]) for r in main]
    axes[0].plot(x,ev,color=new,lw=2.4,marker="o",label="Vegas")
    axes[0].axhline(float(h512["historical_expected_tickets_per_entrant"]),color=old,lw=2,ls="--",label="Historical at N=512: 9.75")
    for xx,v in zip(x,ev):
        axes[0].text(xx,v-.4,f"{v:.4f}",ha="center",fontsize=9,color=new)
    axes[0].set_ylim(0,11)
    axes[0].set_ylabel("Expected tickets per entrant")
    axes[0].set_title("Individual expectation",loc="left")
    for n,color in ((512,light),(1024,new)):
        rows = [r for r in summary if r["entrants"]==str(n)]
        axes[1].plot(x,[float(r["expected_total_tickets"]) for r in rows],color=color,lw=2.4,marker="o",label=f"Vegas N={n:,}")
    axes[1].axhline(4992,color=old,lw=2,ls="--",label="Historical fixed funded pool: 4,992")
    axes[1].annotate("2% draws, N=1,024:\n5,538.43 expected",(2,float(main[2]["expected_total_tickets"])),(2.45,3800),fontsize=9,
                     color=new,arrowprops={"arrowstyle":"-","color":new})
    axes[1].set_ylim(0,7800)
    axes[1].yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    axes[1].set_ylabel("Expected field tickets; historical pool is fixed")
    axes[1].set_title("Attendance changes the field total",loc="left")
    for ax in axes:
        draw_axis(ax)
        ax.legend(frameon=False,loc="upper right",fontsize=8.5)
    fig.suptitle("Ticket expectations decline, while attendance still changes the comparison",x=.075,y=.97,ha="left",fontsize=15,fontweight="bold")
    fig.subplots_adjust(left=.075,right=.97,bottom=.20,top=.82,wspace=.27)
    save(fig,"expected_tickets","Attendance is hypothetical: 512 and 1,024 are Vegas scenarios; the historical advertised cap was 512.\n"
         "Vegas totals are expectations, not maxima or physical claims. All historical Top 128 awards are assumed funded.")

    distribution = read_csv(tables/TABLE_NAMES[1])
    colors = ("#216B8D","#5C926A","#BB8435","#965B83")
    fig,axes = plt.subplots(1,2,figsize=(12,6.2),gridspec_kw={"width_ratios":[1.15,3.7]})
    awards = [10,20,25,30,35,40,50,60,70,80]
    for i,(scenario,color) in enumerate(zip([r["draw_scenario"] for r in main],colors)):
        rows = [r for r in distribution if r["draw_scenario"]==scenario]
        lookup = {int(r["tickets"]):float(r["probability"]) for r in rows}
        axes[0].bar(i,lookup[0],color=color,width=.7)
        axes[0].text(i,lookup[0]+.008,f"{lookup[0]:.2%}",ha="center",fontsize=8,color=color,rotation=0)
        for j,award in enumerate(awards):
            if lookup[award]:
                axes[1].bar(j+(i-1.5)*.2,lookup[award],width=.19,color=color,label=f"{x[i]:g}% draws" if award==20 else None)
    axes[0].set_ylim(.75,.825)
    axes[0].set_xticks(range(4),["0%","1%","2%","5%"])
    axes[0].set_xlabel("Draw probability")
    axes[0].set_title("Zero-ticket probability",loc="left")
    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[1].set_yscale("log")
    axes[1].set_ylim(.000005,.22)
    axes[1].set_yticks([.00001,.0001,.001,.01,.1],["0.001%","0.01%","0.1%","1%","10%"])
    axes[1].set_xticks(range(len(awards)),awards)
    axes[1].set_xlabel("Individual ticket award")
    axes[1].set_ylabel("Probability (log scale)")
    axes[1].set_title("All published positive awards",loc="left")
    axes[1].legend(frameon=False,fontsize=8.5,ncol=2)
    for ax in axes:
        ax.grid(axis="y",alpha=.18)
        ax.set_axisbelow(True)
    fig.suptitle("Draws activate intermediate prize tiers but reduce the 40-ticket chance",x=.075,y=.97,ha="left",fontsize=15,fontweight="bold")
    fig.subplots_adjust(left=.075,right=.98,bottom=.20,top=.82,wspace=.30)
    save(fig,"ticket_distribution","Exact analytical distributions, independent of attendance in this marginal model. Zero panel has a truncated axis.\n"
         "At 0% draws the 10, 25, 35, 50 and 70 tiers have zero probability; complete fractions are retained in CSV.")

    outcomes = read_csv(tables/TABLE_NAMES[3])
    terminal = [r for r in outcomes if r["round"]=="11" and r["outcome"]=="draw"]
    scores = sorted({int(r["a_start_points"]) for r in terminal})
    lookup = {(int(r["a_start_points"]),int(r["b_start_points"])):r for r in terminal}
    fields = ("draw_minus_a_win_combined_tickets","draw_minus_b_win_combined_tickets")
    limit = max(abs(int(r[field])) for r in terminal for field in fields)
    fig,axes = plt.subplots(1,2,figsize=(11.8,6.6))
    for ax,field,label in zip(axes,fields,("Draw minus A wins","Draw minus B wins")):
        values = [[int(lookup[a,b][field]) for b in scores] for a in scores]
        im = ax.imshow(values,cmap="RdBu",norm=TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit),origin="lower")
        for i,row in enumerate(values):
            for j,v in enumerate(row):
                ax.text(j,i,f"{v:+d}" if v else "0",ha="center",va="center",fontsize=9,color="white" if abs(v)>limit*.65 else "#202020")
            ax.add_patch(Rectangle((i-.48,i-.48),.96,.96,fill=False,edgecolor="#292929",lw=1))
        ax.set_xticks(range(len(scores)),scores)
        ax.set_yticks(range(len(scores)),scores)
        ax.set_xlabel("Player B points before Round 11")
        ax.set_ylabel("Player A points before Round 11")
        ax.set_title(label+" (combined tickets)",loc="left")
    fig.colorbar(im,ax=axes.ravel().tolist(),fraction=.025,pad=.025,label="Ticket difference",ticks=sorted({-limit,-5,0,5,limit}))
    fig.suptitle("Round 11: equal-score outcomes conserve tickets; unequal scores can differ",x=.075,y=.97,ha="left",fontsize=14,fontweight="bold")
    fig.subplots_adjust(left=.075,right=.86,bottom=.23,top=.84,wspace=.33)
    # Position colorbar after adjusting the main axes to keep all labels clear.
    fig.axes[-1].set_position([.90,.27,.02,.51])
    save(fig,"round11_outcomes","Positive = the draw awards more combined tickets than that decisive outcome; boxes mark equal scores.\n"
         "Scores have individually feasible no-prior-draw paths through the Day 2 cut. Joint Swiss pairings/frequencies are not verified.")

    gate = [r for r in outcomes if r["round"]=="6" and r["future_draw_scenario"]=="draw-0pct"]
    gate_scores = sorted({int(r["a_start_points"]) for r in gate})
    lookup = {(r["outcome"],int(r["a_start_points"]),int(r["b_start_points"])):int(r["qualified_players"]) for r in gate}
    fig,axes = plt.subplots(1,3,figsize=(12.5,5.9))
    for ax,outcome,label in zip(axes,("a_win","draw","b_win"),("A wins","Draw","B wins")):
        values = [[lookup[outcome,a,b] for b in gate_scores] for a in gate_scores]
        im = ax.imshow(values,cmap="Blues",vmin=0,vmax=2,origin="lower")
        for i,row in enumerate(values):
            for j,v in enumerate(row):
                ax.text(j,i,str(v),ha="center",va="center",fontsize=10,color="white" if v==2 else "#202020")
        index = gate_scores.index(9)
        ax.add_patch(Rectangle((index-.48,index-.48),.96,.96,fill=False,edgecolor="#C35C28",lw=2))
        ax.set_xticks(range(len(gate_scores)),gate_scores)
        ax.set_yticks(range(len(gate_scores)),gate_scores)
        ax.set_xlabel("Player B points before Round 6")
        ax.set_ylabel("Player A points before Round 6")
        ax.set_title(label,loc="left")
    fig.suptitle("Round 6: at 9–9 points, a draw eliminates both; a decisive result advances one",x=.075,y=.97,ha="left",fontsize=14,fontweight="bold")
    fig.subplots_adjust(left=.065,right=.98,bottom=.23,top=.83,wspace=.35)
    save(fig,"round6_qualification","Cells count Day 2 qualifiers (0, 1 or 2), not ticket recipients. Orange boxes mark the 9–9 case.\n"
         "Future ticket EV is separate in the CSV and depends on the specified Sunday W/D/L probabilities. No pairing frequencies are modeled.")

    write_json(output/"saturday_draw_manifest.json",{"matplotlib_version":matplotlib.__version__,
               "renderer_sha256":sha256(Path(__file__)),
               "input_sha256":{"outputs/tables/"+name:sha256(tables/name) for name in TABLE_NAMES},
               "figure_sha256":{name:sha256(root/name) for name in files},
               "scope":"Phase 3B independent draw scenarios and conditional local outcomes only; earlier figures untouched"})
    return files
