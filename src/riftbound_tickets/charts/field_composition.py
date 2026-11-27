"""One distinct Phase 6 finding: aggregate historical registry overlap."""
import os
from pathlib import Path
from ..phase3a import read_csv,write_json,sha256


def render_figures(root):
    root=Path(root).resolve();os.environ.setdefault('MPLCONFIGDIR',str(root/'.cache/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,
        'figure.facecolor':'#FBFAF7','axes.facecolor':'#FBFAF7','svg.hashsalt':'phase6-composition'})
    rows=read_csv(root/'outputs/tables/phase6_composition.csv')
    pooled=read_csv(root/'outputs/tables/phase6_weekday_summary.csv')
    cities=['atlanta','sydney','vancouver','utrecht','hartford','barcelona','singapore','los-angeles']
    fig,ax=plt.subplots(figsize=(16,9));colors=['#216B8D','#A45925','#75814C']
    for offset,day,color in zip((-.22,0,.22),('friday','saturday','sunday'),colors):
        values=[float(next(r['fraction_of_side_standings'] for r in rows if r['event_key']==city+'-'+day and r['identity_group']=='main_registry_linked')) for city in cities]
        y=[i+offset for i in range(8)];ax.barh(y,values,height=.20,color=color,label=day.title())
    ax.set_yticks(range(8),[c.replace('-',' ').title() for c in cities]);ax.invert_yaxis()
    ax.set_xlim(0,1.03);ax.xaxis.set_major_formatter(PercentFormatter(1));ax.grid(axis='x',alpha=.16);ax.set_axisbelow(True)
    ax.set_xlabel('Share of side-event standings entries linked to the same-city main-event registry',labelpad=14)
    ax.legend(loc='lower right',frameon=False,fontsize=13)
    fig.suptitle('Historical Saturday side fields had little main-event overlap',x=.105,y=.95,ha='left',fontsize=22,fontweight='bold')
    fig.text(.105,.885,'Pooled registry overlap: '+ '    •    '.join(f"{r['weekday'].title()} {float(r['main_registry_fraction']):.1%}" for r in pooled),fontsize=15)
    fig.subplots_adjust(left=.105,right=.96,top=.80,bottom=.23)
    fig.text(.105,.04,'Exact stable-ID linkage across eight cities. Denominators: 11,571 Friday / 3,165 Saturday / 5,915 Sunday standings entries.\n'
        'Six side entries have unresolved identity linkage; no display-name matching. Registry overlap is not physical attendance or measured skill.\n'
        'Scheduling and participation are associated; these data do not establish a causal field-strength effect or the weakest Vegas day.',fontsize=10.5,linespacing=1.5)
    files=[]
    for ext in ('svg','png'):
        p=root/f'outputs/figures/phase6_field_composition.{ext}'
        fig.savefig(p,dpi=120,metadata={'Date':None} if ext=='svg' else {'Software':'Matplotlib '+matplotlib.__version__})
        files.append(str(p.relative_to(root)))
    plt.close(fig)
    inputs=['outputs/tables/phase6_composition.csv','outputs/tables/phase6_weekday_summary.csv']
    write_json(root/'outputs/figures/phase6_manifest.json',{'figure_sha256':{p:sha256(root/p) for p in files},
        'input_sha256':{p:sha256(root/p) for p in inputs},
        'renderer_sha256':{'src/riftbound_tickets/charts/field_composition.py':sha256(Path(__file__))},
        'canvas':'1920x1080 PNG and vector SVG','matplotlib_version':matplotlib.__version__})
    return files
