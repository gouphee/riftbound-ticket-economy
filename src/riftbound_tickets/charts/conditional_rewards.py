"""Two video figures, drawn exclusively from the additive machine tables."""
import os
from pathlib import Path
from ..phase3a import read_csv, sha256, write_json


def render_figures(root):
    root=Path(root).resolve();os.environ.setdefault('MPLCONFIGDIR',str(root/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':14,
        'axes.titleweight':'bold','axes.spines.top':False,'axes.spines.right':False,
        'figure.facecolor':'#FBFAF7','axes.facecolor':'#FBFAF7','svg.hashsalt':'conditional-rewards-v1'})
    old,new,split='#A45925','#216B8D','#75814C'
    inputs=('conditional_record_probabilities.csv','conditional_historical_hybrid_rewards.csv',
        'conditional_historical_record_cohorts.csv','conditional_vegas_final_round_rewards.csv')
    tables={n:read_csv(root/'outputs/tables'/n) for n in inputs};files=[]
    def save(fig,name,footer):
        fig.text(.065,.035,footer,fontsize=10,color='#505050',va='bottom',linespacing=1.5)
        for ext in ('svg','png'):
            path=root/f'outputs/figures/conditional_{name}.{ext}'
            fig.savefig(path,dpi=120,metadata={'Date':None} if ext=='svg' else {'Software':'Matplotlib '+matplotlib.__version__})
            files.append(str(path.relative_to(root)))
        plt.close(fig)
    rows=[r for r in tables[inputs[0]] if float(r['draw_probability_d'])==0]
    ps=[float(r['decisive_win_probability_p']) for r in rows]
    fig,axes=plt.subplots(1,3,figsize=(16,9))
    pairs=(('historical_exact_5_1','vegas_exact_8_2','Exact record','5–1 after 6','8–2 after 10'),
        ('historical_at_least_5_wins','vegas_at_least_8_wins','Record or better','5+ wins after 6','8+ wins after 10'),
        ('historical_exact_6_0','vegas_exact_10_0','Perfect run','6–0 after 6','10–0 after 10'))
    for ax,(a,b,title,la,lb) in zip(axes,pairs):
        ax.plot(ps,[float(r[a]) for r in rows],'-o',lw=3,color=old,label=la)
        ax.plot(ps,[float(r[b]) for r in rows],'-o',lw=3,color=new,label=lb)
        ax.set_title(title,loc='left',pad=18);ax.set_xlabel('Hypothetical match win probability')
        ax.xaxis.set_major_formatter(PercentFormatter(1));ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.set_xticks(ps);ax.grid(alpha=.18);ax.legend(frameon=False,loc='upper left',fontsize=11)
        ax.set_xlim(.38,.82);ax.set_ylim(0,.75 if a!='historical_exact_6_0' else .30)
    axes[0].set_ylabel('Probability per entrant')
    axes[1].annotate('At 80%, the cumulative\ncomparison reverses',xy=(.8,.6778),xytext=(.48,.51),
        fontsize=11,arrowprops={'arrowstyle':'-','color':new},color=new)
    fig.suptitle('Stronger records are rarer — but “or better” depends on skill',x=.065,y=.94,ha='left',fontsize=21,fontweight='bold')
    fig.text(.065,.875,'Historical: Round 6 checkpoint of 7 Swiss rounds     •     Vegas: Round 10 checkpoint of 11 rounds',fontsize=13)
    fig.subplots_adjust(left=.065,right=.975,top=.77,bottom=.24,wspace=.28)
    save(fig,'record_difficulty','Exact iid no-draw model; fixed p across rounds, no byes or drops. Vegas applies the ≥12-point Round 6 gate.\n'
        'Every shown Vegas target necessarily passes that gate. Reaching a record does not establish historical cut qualification or ticket issuance.')

    hybrid=[r for r in tables[inputs[1]] if r['event_key']=='all_eight_events']
    fig,axes=plt.subplots(1,2,figsize=(16,9),sharey=True)
    records=['5-1-0','6-0-0']
    pick=lambda record,q,arr:next(float(r['conditional_expected_tickets']) for r in hybrid
        if r['record']==record and float(r['future_bracket_win_probability_q'])==q and r['arrangement']==arr)
    mean=[pick(r,.5,'published') for r in records]
    low=[pick(r,.4,'published') for r in records];high=[pick(r,.8,'published') for r in records]
    ax=axes[0];xs=[0,1]
    ax.fill_between(xs,low,high,color=old,alpha=.14,label='Future bracket q = 40–80% (model range)')
    ax.plot(xs,mean,color=old,lw=3,marker='o',ms=9,label='Published bracket, q = 50% (hybrid model)')
    ax.plot(xs,[pick(r,.5,'top8_equal') for r in records],color=split,lw=2,ls='--',label='Hypothetical 216 each once in Top 8')
    for x,y,cut in zip(xs,mean,('16 / 216 into Top 8','36 / 37 into Top 8')):
        ax.annotate(f'{y:.1f} tickets\n{cut}',(x,y),(x+.04,y+18),fontsize=12,color=old)
    ax.set_xticks(xs,['5–1 after 6','6–0 after 6']);ax.set_xlim(-.16,1.55)
    ax.set_title('Historical Saturday: cut conversion matters',loc='left',pad=20)
    ax.set_xlabel('Entering the last Swiss round')
    ax.set_ylabel('Conditional expected tickets');ax.legend(frameon=False,loc='upper left',fontsize=10)
    vr=[r for r in tables[inputs[3]] if float(r['draw_probability_d'])==0]
    vrecords=['8-2-0','9-1-0','10-0-0']
    vp=lambda record,p:next(r for r in vr if r['checkpoint_record']==record and float(r['decisive_win_probability_p'])==p)
    values=[float(vp(r,.5)['expected_tickets']) for r in vrecords]
    vlow=[float(vp(r,.4)['expected_tickets']) for r in vrecords];vhigh=[float(vp(r,.8)['expected_tickets']) for r in vrecords]
    ax=axes[1];xs=[0,1,2]
    ax.fill_between(xs,vlow,vhigh,color=new,alpha=.18,label='Final-match p = 40–80% (model range)')
    ax.plot(xs,values,'-o',lw=3,ms=9,color=new,label='Expected reward at final-match p = 50%')
    floors=[int(vp(r,.5)['guaranteed_tickets_if_completed_eligible']) for r in vrecords]
    caps=[int(vp(r,.5)['maximum_possible_tickets']) for r in vrecords]
    ax.errorbar(xs,values,yerr=[[v-f for v,f in zip(values,floors)],[c-v for v,c in zip(values,caps)]],
        fmt='none',ecolor=new,capsize=8,lw=1.4,label='Loss-to-win guaranteed / maximum range')
    for x,y in zip(xs,values):ax.text(x,y+18,f'{y:.0f} tickets',ha='center',color=new,fontsize=13)
    ax.set_xticks(xs,['8–2 after 10','9–1 after 10','10–0 after 10']);ax.set_xlim(-.25,2.25)
    ax.set_title('Vegas Rebound: one match remains',loc='left',pad=20)
    ax.set_xlabel('Entering Round 11');ax.legend(frameon=False,loc='upper left',fontsize=10)
    for ax in axes:ax.set_ylim(0,350);ax.grid(axis='y',alpha=.18)
    fig.suptitle('The conditional reward curve is much lower in Vegas',x=.065,y=.94,ha='left',fontsize=22,fontweight='bold')
    fig.text(.065,.88,'Same vertical scale; these are different record checkpoints, not matched finishing percentiles.',fontsize=13)
    fig.subplots_adjust(left=.065,right=.975,top=.78,bottom=.25,wspace=.18)
    save(fig,'reward_curve','Historical hybrid: observed R6→R7 outcomes held fixed; only future cut matches vary with q. Cut fractions describe eight events.\n'
        'The 216-each split is hypothetical for this cohort; it equals the published-bracket mean at q = 50%. Shading is not a guarantee.\n'
        'Vegas ranges assume completion and eligibility. A secured historical Top 8 slot guaranteed 144; Vegas’s overall maximum is 80. Issuance unverified.')
    write_json(root/'outputs/figures/conditional_manifest.json',{'figure_sha256':{p:sha256(root/p) for p in files},
        'input_sha256':{'outputs/tables/'+p:sha256(root/'outputs/tables'/p) for p in inputs},
        'renderer_sha256':{'src/riftbound_tickets/charts/conditional_rewards.py':sha256(Path(__file__))},
        'canvas':'1920x1080 PNG plus vector SVG','matplotlib_version':matplotlib.__version__})
    return files
