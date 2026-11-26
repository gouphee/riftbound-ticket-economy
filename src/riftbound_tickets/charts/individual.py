"""Publication figures from Phase 4 machine-readable outputs only."""
from __future__ import annotations
import os
from pathlib import Path
from ..phase3a import read_csv,sha256,write_json

LABELS={'sunday_only':'Sunday Challenge','competitive_first':'Competitive first','saturday_first':'Saturday first',
        'casual_focused':'Casual focused','mixed':'Mixed Riftbound','ode_constructed':'Constructed ODEs',
        'ode_tft_normal':'TFT Normal ODEs','mixed_with_tft':'Mixed + TFT','ticket_aware_adaptive':'Adaptive menu'}


def render_figures(root):
    root=Path(root).resolve()
    os.environ.setdefault('MPLCONFIGDIR',str(root/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
        'axes.titlesize':12,'axes.titleweight':'bold','figure.facecolor':'#FBFAF7','axes.facecolor':'#FBFAF7',
        'svg.hashsalt':'riftbound-phase4'})
    colors=['#216B8D','#A45925','#5C926A','#965B83','#BB8435','#477481']
    tables=root/'outputs/tables'; output=root/'outputs/figures'; output.mkdir(exist_ok=True)
    def rows(name): return read_csv(tables/f'phase4_{name}.csv')
    def primary(r): return float(r['conditional_decisive_win_probability'])==.5 and float(r['competitive_draw_rate'])==0 and float(r['bo1_draw_rate'])==0
    econ=[r for r in rows('event_economics') if primary(r)]
    strategies=[r for r in rows('strategy_results') if primary(r)]
    files=[]
    def save(fig,name,footer):
        fig.text(.07,.025,footer,fontsize=8,va='bottom',ha='left',color='#505050')
        for ext in ('svg','png'):
            path=output/f'phase4_{name}.{ext}'
            fig.savefig(path,dpi=200,metadata={'Date':None} if ext=='svg' else {'Software':'Matplotlib '+matplotlib.__version__})
            files.append(str(path.relative_to(root)))
        plt.close(fig)
    names={'ode-standard-constructed':'Constructed ODE','friday-super-nexus-night':'Nexus Night',
           'friday-radiance-sealed-deck':'Scheduled sealed','sunday-radiance-standard-challenge':'Sunday Challenge',
           'saturday-standard-rebound-day-1':'Saturday Rebound (two days)','ode-tft-normal':'TFT Normal ODE',
           'friday-champion-deck-trial':'Champion Deck Trial','ode-radiance-draft':'Draft ODE'}
    pmfs=rows('event_distributions')
    fig,axes=plt.subplots(2,3,figsize=(12,7.5))
    for ax,(event,label),color in zip(axes.flat,list(names.items())[:6],colors):
        data=sorted([r for r in pmfs if r['event_id']==event and primary(r)],key=lambda r:int(r['tickets']))
        ax.bar(range(len(data)),[float(r['probability']) for r in data],color=color,width=.7)
        ax.set_xticks(range(len(data)),[r['tickets'] for r in data],fontsize=8)
        ax.set_ylim(0,1)
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.set_xlabel('Tickets awarded');ax.set_title(label,loc='left');ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    fig.suptitle('Most solo events award a few tickets; competitive events carry a long tail',x=.07,y=.98,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.07,right=.98,bottom=.19,top=.88,hspace=.55,wspace=.28)
    save(fig,'event_distributions','Equal-skill / no-draw marginal benchmarks. TFT uses exchangeable finish ranks, independently of Riftbound skill.\nPublished individual awards; team prizes and discretionary honor tickets excluded. Tickets do not guarantee redemption.')

    selected=[next(r for r in econ if r['event_id']==key) for key in names]
    fig,axes=plt.subplots(1,2,figsize=(12,6.7),sharey=True)
    for ax,field,title in zip(axes,('tickets_per_entry_dollar','tickets_per_elapsed_hour'),('Expected tickets per entry dollar','Expected tickets per published event hour')):
        values=[float(r[field]) for r in selected]
        ax.barh(range(len(selected)),values,color=colors[0])
        ax.set_yticks(range(len(selected)),names.values());ax.invert_yaxis()
        for i,value in enumerate(values): ax.text(value+.015*max(values),i,f'{value:.3f}',va='center',fontsize=9)
        ax.set_xlim(0,max(values)*1.25);ax.set_title(title,loc='left');ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
    fig.suptitle('Sunday Challenge has the highest expected ticket yield per entry dollar',x=.07,y=.97,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.27,right=.98,bottom=.20,top=.86,wspace=.15)
    save(fig,'event_efficiency','Entry-fee-only, equal-skill / no draws. Products retained separately without monetary credit.\nHours exclude ODE queues and fixed-event check-in here; weekend models add them. Rebound reserves both stages when qualified.')

    all_results=rows('strategy_results')
    keys=['sunday_only','competitive_first','mixed','ticket_aware_adaptive']
    fig,ax=plt.subplots(figsize=(11,6.8))
    for key,color in zip(keys,colors):
        data=sorted([r for r in all_results if r['strategy']==key and float(r['competitive_draw_rate'])==0
                    and r['performance_scope']=='same_hypothetical_p_per_Riftbound_format_TFT_exchangeable'],key=lambda r:float(r['conditional_decisive_win_probability']))
        ax.plot([float(r['conditional_decisive_win_probability']) for r in data],[float(r['p_at_least_40']) for r in data],marker='o',lw=2.2,color=color,label=LABELS[key])
    ax.yaxis.set_major_formatter(PercentFormatter(1));ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel('Hypothetical conditional decisive-match win probability in each Riftbound format')
    ax.set_ylabel('Probability of accumulating at least 40 tickets');ax.set_ylim(0,1)
    ax.grid(alpha=.18);ax.legend(frameon=False,loc='upper left')
    fig.suptitle('Performance and event choices change individual success substantially',x=.07,y=.97,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.10,right=.97,bottom=.22,top=.87)
    save(fig,'performance','No-draw sensitivity, not fitted player forecasts. Constant high win rates can overstate later Swiss performance.\nAll schedules require available seats/pods; adaptive menu has a $200 entry cap and 30 occupied-hour cap.')

    fig,axes=plt.subplots(1,3,figsize=(14,7.2))
    chosen=['sunday_only','competitive_first','saturday_first','mixed','casual_focused','ode_constructed','ticket_aware_adaptive']
    handles=[]
    fields=('expected_entry_fee_usd','expected_occupied_hours','expected_calendar_span_hours')
    titles=('Expected entry spending (USD)','Expected occupied hours','Calendar elapsed hours from Friday 11:00')
    for ax,field,title in zip(axes,fields,titles):
        for i,key in enumerate(chosen):
            r=next(r for r in strategies if r['strategy']==key)
            x,y=float(r[field]),float(r['p_at_least_40'])
            point=ax.scatter(x,y,s=65,color=colors[i%len(colors)],zorder=3,label=f'{i+1}  {LABELS[key]}')
            if ax is axes[0]: handles.append(point)
            ax.annotate(str(i+1),(x,y),(6,6),textcoords='offset points',fontsize=9)
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(-.01,.235)
        ax.set_xlabel(title,fontsize=9);ax.set_ylabel('Probability of at least 40 tickets');ax.grid(alpha=.18)
        ax.margins(x=.12)
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.53,.105),ncol=4,frameon=False,fontsize=9)
    fig.suptitle('Money, occupied time and calendar time measure different acquisition costs',x=.07,y=.97,ha='left',fontsize=14,fontweight='bold')
    fig.subplots_adjust(left=.065,right=.98,bottom=.29,top=.84,wspace=.40)
    save(fig,'cost_time_success','Equal-skill / no draws, published durations, 15-minute ODE queues; stop after event settlement reaches 40.\nUnconditional means include failures. Calendar hours include overnight gaps; festival pass, travel, lodging and decks excluded.')

    start=rows('starting_tickets')
    options=['ode-standard-constructed','friday-super-nexus-night','friday-radiance-sealed-deck',
             'sunday-radiance-standard-challenge','saturday-standard-rebound-day-1','ode-tft-normal']
    values=[]
    for key in options:
        values.append([float(next(r for r in start if r['event_id']==key and r['starting_tickets']==str(t))['p_at_least_40']) for t in (0,10,20,25,30,35)])
    fig,ax=plt.subplots(figsize=(11,6.6))
    im=ax.imshow(values,cmap='Blues',vmin=0,vmax=.6,aspect='auto')
    for i,line in enumerate(values):
        for j,value in enumerate(line): ax.text(j,i,f'{value:.1%}',ha='center',va='center',color='white' if value>.35 else '#202020')
    ax.set_yticks(range(len(options)),[names[x] for x in options]);ax.set_xticks(range(6),[0,10,20,25,30,35])
    ax.set_xlabel('Tickets already held before the event');fig.colorbar(im,ax=ax,pad=.03,label='Chance of reaching 40 after one event')
    fig.suptitle('The remaining ticket gap changes which event can help',x=.07,y=.97,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.29,right=.95,bottom=.21,top=.85)
    save(fig,'starting_tickets','Equal skill / no draws. Standalone opportunities before their starts; availability, budget and duration still constrain choice.\nAt 35 tickets, scheduled sealed and Sunday Challenge each succeed 50%; sealed takes 3 hours versus 7.5 hours.')

    defs=rows('strategy_definitions')
    fig,axes=plt.subplots(1,3,figsize=(13,6.5),sharey=True)
    lanes=[('Mixed Riftbound','mixed',None),('Competitive: qualifies','competitive_first',True),('Competitive: eliminated','competitive_first',False)]
    for day,ax in enumerate(axes):
        for lane,(label,key,qual) in enumerate(lanes):
            for r in defs:
                if r['strategy']!=key or int(r['day'])!=day: continue
                if qual is not None and (r['branch']=='only_if_qualified' and not qual or r['branch']=='only_if_not_qualified' and qual): continue
                start_min,end=float(r['start_including_queue_or_checkin_minute']),float(r['end_minute'])
                ax.barh(lane,(end-start_min)/60,left=start_min/60,height=.55,color=colors[0 if key=='mixed' else 1])
                event=r['event_id'].split('-',1)[1].replace('radiance-','').replace('standard-','').replace('super-','').replace('-day-1','').replace('-day-2','')
                event={'nexus-night':'Nexus','rebound':'Rebound','challenge':'Challenge','champion-deck-trial':'Trial','standard-constructed':'ODE'}.get(event,event)
                if end-start_min>120: ax.text((start_min+end)/120,lane,event,ha='center',va='center',color='white',fontsize=8)
        ax.set_xlim(10.5,21.75);ax.set_xticks([11,14,17,20],['11:00','14:00','17:00','20:00']);ax.set_xlabel('Las Vegas local time')
        ax.set_title(['Friday Dec 11','Saturday Dec 12','Sunday Dec 13'][day],loc='left');ax.grid(axis='x',alpha=.15)
    axes[0].set_yticks(range(3),[x[0] for x in lanes]);axes[0].invert_yaxis()
    fig.suptitle('Sunday qualification changes which opportunities remain available',x=.07,y=.97,ha='left',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.18,right=.98,bottom=.22,top=.83,wspace=.12)
    save(fig,'weekend_schedule','Published event windows, 15-minute check-in/queues and breaks. Later visits are skipped once 40 tickets settle.\nRebound occupies Saturday through 20:00; qualifiers continue Sunday, while nonqualifiers may enter Sunday Challenge if seats remain.')

    constraints=rows('budget_time_constraints'); budgets=[50,100,150,200,250]; hours=[10,20,30]
    fig,ax=plt.subplots(figsize=(10,5.8))
    vals=[[float(next(r for r in constraints if int(r['entry_budget_usd'])==b and int(r['occupied_hour_budget'])==h)['p_at_least_40']) for b in budgets] for h in hours]
    im=ax.imshow(vals,vmin=0,vmax=.2,cmap='Blues',aspect='auto')
    for i,line in enumerate(vals):
        for j,value in enumerate(line): ax.text(j,i,f'{value:.1%}',ha='center',va='center',color='white' if value>.12 else '#202020')
    ax.set_xticks(range(len(budgets)),[f'${b}' for b in budgets]);ax.set_yticks(range(3),hours)
    ax.set_xlabel('Hard entry-fee budget');ax.set_ylabel('Hard occupied-hour budget');fig.colorbar(im,ax=ax,label='Probability of 40 tickets')
    fig.suptitle('A finite adaptive menu shows the effect of hard resource limits',x=.07,y=.97,ha='left',fontsize=14,fontweight='bold')
    fig.subplots_adjust(left=.12,right=.95,bottom=.22,top=.84)
    save(fig,'budget_time','Equal-skill / no draws; policy reoptimized under each hard constraint, including failed attempts.\nThis is the declared Riftbound menu only, conditional on admission. It is not a global weekend optimum.')

    write_json(output/'phase4_manifest.json',{'matplotlib_version':matplotlib.__version__,
        'renderer_sha256':{'src/riftbound_tickets/charts/individual.py':sha256(Path(__file__))},
        'input_sha256':{str(p.relative_to(root)):sha256(p) for p in sorted(tables.glob('phase4_*.csv'))},
        'figure_sha256':{p:sha256(root/p) for p in files}})
    return files
