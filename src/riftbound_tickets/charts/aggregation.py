"""Four focused Phase 5 figures from audited machine-readable tables."""
import os
from pathlib import Path
from ..phase3a import read_csv,sha256,write_json


def render_figures(root):
    root=Path(root).resolve();tables=root/'outputs/tables';out=root/'outputs/figures';out.mkdir(exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR',str(root/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
        'axes.titleweight':'bold','figure.facecolor':'#FBFAF7','axes.facecolor':'#FBFAF7','svg.hashsalt':'riftbound-phase5'})
    old,new='#A45925','#216B8D'
    files=[]
    def read(name):return read_csv(tables/f'phase5_{name}.csv')
    def save(fig,name,footer):
        fig.text(.075,.025,footer,fontsize=8,color='#505050',va='bottom')
        for ext in ('svg','png'):
            p=out/f'phase5_{name}.{ext}';fig.savefig(p,dpi=200,metadata={'Date':None} if ext=='svg' else {'Software':'Matplotlib '+matplotlib.__version__});files.append(str(p.relative_to(root)))
        plt.close(fig)
    data=[r for r in read('saturday_comparison') if r['vegas_draw_rate_exact']=='0' and r['historical_allocation']=='historical_official' and r['group_size']!='1']
    x=[int(r['group_size']) for r in data]
    fig,axes=plt.subplots(1,2,figsize=(12,6.4))
    for prefix,label,color in [('historical','Historical Saturday',old),('vegas','Vegas Rebound',new)]:
        y=[100*float(r[prefix+'_incremental_success_probability']) for r in data]
        axes[0].plot(x,y,marker='o',lw=2.3,label=label,color=color)
        for xx,yy in zip(x,y):
            offset=(10,14 if prefix=='vegas' else 4) if xx==2 else (0,10 if prefix=='vegas' else -18)
            axes[0].annotate(f'+{yy:.2f} pp',(xx,yy),offset,textcoords='offset points',ha='left' if xx==2 else 'center',fontsize=9,color=color,
                             bbox={'facecolor':'#FBFAF7','edgecolor':'none','pad':1})
        axes[1].plot(x,[float(r[prefix+'_relative_success_lift']) for r in data],marker='o',lw=2.3,color=color,label=label)
    axes[0].set_ylabel('Added success probability (percentage points)');axes[0].set_title('Absolute pooling increment',loc='left')
    axes[1].set_ylabel('Relative increase over no pooling');axes[1].yaxis.set_major_formatter(PercentFormatter(1));axes[1].set_title('Relative pooling advantage',loc='left')
    for ax in axes:
        ax.set_xticks(x);ax.set_xlabel('Participants in the group');ax.set_ylim(bottom=0);ax.grid(alpha=.18);ax.legend(frameon=False)
    fig.suptitle('Pooling adds more to the 40-ticket chance under the Vegas benchmark',x=.075,y=.97,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.085,right=.97,bottom=.22,top=.82,wspace=.30)
    save(fig,'pooling_advantage','Matched attendance N=512, equal skill / no draws. Historical ranks sampled without replacement; Vegas uses independent marginal awards.\nFull pooling is a permission-dependent counterfactual. Absolute pooled success remains lower in Vegas for groups of 2, 4 and 8.')

    groups=read('saturday_groups')
    fig,ax=plt.subplots(figsize=(11,6.5))
    for event,color,label,sampling in [('historical_official',old,'Historical','without_replacement'),('vegas_rebound',new,'Vegas','independent')]:
        selected=[r for r in groups if r['event_model']==event and r['draw_rate_exact']=='0' and r['sampling']==sampling]
        for field,ls,kind in [('units_no_pool_per_participant','--','No pooling'),('units_full_pool_per_participant','-','Full pooling')]:
            ax.plot([int(r['group_size']) for r in selected],[float(r[field]) for r in selected],color=color,ls=ls,lw=2.3,marker='o',label=f'{label}: {kind}')
    ax.set_xticks([1,2,4,8]);ax.set_xlabel('Participants in the group');ax.set_ylabel('Expected complete 40-ticket units per participant')
    ax.set_ylim(0,.22);ax.grid(alpha=.18);ax.legend(frameon=False,loc='upper left')
    fig.suptitle('Greater success advantage does not imply more ticket capacity',x=.075,y=.97,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.10,right=.97,bottom=.22,top=.86)
    save(fig,'units_per_participant','Potential ticket units, not redeemed metals; inventory, eligibility and badge limits are unresolved.\nN=512, equal skill / no draws; historical ranks sampled without replacement, Vegas independent marginal awards.\nAt eight participants, the per-person capacity increment is slightly smaller in Vegas despite its larger success-probability increment.')

    friday=read('friday_comparison')
    keys=['friday-super-nexus-night','friday-radiance-sealed-deck','friday-champion-deck-trial','friday-draft-challenge','friday-radiance-2v2-team-challenge']
    labels=['Nexus Night\n$25 entry','Sealed\n$50 entry','Champion Trial\n$25 entry','Draft Challenge\n$25 entry','2v2 equal allocation\nUSD 25 or 50 per person*']
    selected=[next(r for r in friday if r['event_id']==key) for key in keys]
    fig,axes=plt.subplots(1,3,figsize=(13.5,6.4),sharey=True)
    for ax,field,title in zip(axes,('expected_tickets_person','occupied_hours','p40_person'),('Expected tickets per person','Occupied hours per person','Chance of 40 tickets per person')):
        values=[float(r[field]) for r in selected]
        ax.barh(range(5),values,color=[old]*4+[new],height=.64)
        ax.set_yticks(range(5),labels,fontsize=9);ax.set_title(title,loc='left',fontsize=11)
        ax.set_xlim(0,max(values)*1.32 if max(values) else 1);ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
        if field=='p40_person':ax.xaxis.set_major_formatter(PercentFormatter(1))
        for i,v in enumerate(values):ax.text(v+max(values)*.025,i,f'{v:.3%}' if field=='p40_person' else f'{v:.2f}',va='center',fontsize=9)
    axes[0].invert_yaxis()
    fig.suptitle('Friday 2v2 adds a ticket tail with a longer time commitment',x=.075,y=.97,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.24,right=.97,bottom=.24,top=.84,wspace=.25)
    save(fig,'friday_team','Equal skill / no draws; 2v2 team-win probability is specified directly, independently of solo performance.\n*Friday $50 fee basis and team allocation are unverified. Integer equal division is hypothetical. 2v2 conflicts with Friday Nexus.')

    ode=[r for r in read('ode_comparison') if r['decisive_win_probability_exact']=='1/2' and r['throughput_basis']=='published_durations']
    fig,axes=plt.subplots(1,3,figsize=(12.5,6.1))
    fields=('single_pod_expected_tickets','single_pod_expected_tickets_per_published_hour','p_at_least_40')
    titles=('Same mean per completed pod','Different published time cost','Rare 40-ticket tail in a common horizon')
    for ax,field,title in zip(axes,fields,titles):
        values=[float(r[field]) for r in ode]
        ax.bar([0,1],values,color=[old,new],width=.58)
        ax.set_xticks([0,1],['Historical\ncompetitive ODE','Vegas\nConstructed ODE'],fontsize=9)
        ax.set_title(title,loc='left',fontsize=10.5);ax.set_ylim(0,max(values)*1.4);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
        for xx,v in enumerate(values):ax.text(xx,v+max(values)*.04,f'{v:.3%}' if field=='p_at_least_40' else f'{v:.2f}',ha='center',fontsize=10)
        if field=='p_at_least_40':ax.yaxis.set_major_formatter(PercentFormatter(1))
    axes[0].set_ylabel('Expected tickets per entrant');axes[1].set_ylabel('Tickets per published event hour');axes[2].set_ylabel('Probability of accumulating 40 tickets')
    fig.suptitle('The old competitive ODE offered a larger ceiling at the same mean per pod',x=.075,y=.97,ha='left',fontsize=14,fontweight='bold')
    fig.subplots_adjust(left=.075,right=.98,bottom=.25,top=.82,wspace=.38)
    save(fig,'competitive_ode','Equal-skill / no-draw reference: decisive-match p=50% in both formats. Old competitive award: 12 tickets for three consecutive BO3 wins.\nThe Vegas 1/2/3-ticket casual offer also existed in all eight historical schedules. Common windows and 15-minute queues/breaks: five vs eight pods.\nHistorical desk hours are unknown; full published slots reserved, personal stop at 40. These are different offer types, not a newly faster Vegas format.')

    write_json(out/'phase5_manifest.json',{'matplotlib_version':matplotlib.__version__,
        'renderer_sha256':{'src/riftbound_tickets/charts/aggregation.py':sha256(Path(__file__))},
        'input_sha256':{str(p.relative_to(root)):sha256(p) for p in sorted(tables.glob('phase5_*.csv'))},
        'figure_sha256':{p:sha256(root/p) for p in files}})
    return files
