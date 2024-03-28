import matplotlib.pyplot as plt 
import plotly.express as px 
import plotly.graph_objects as go 
from utils.BeneficiaryProfile import Beneficiary
import utils.utils as utils 
import os 
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import copy 

## Parameters and utility functions for making plots 

beneficiary_color_palette =[
"#FFD700", # (Gold)
"#008080", # (Teal)
"#FF6347", # (Tomato)
"#00CED1", # (Dark Turquoise)
]


ben_display_map = {

  # column_name: display_name, display_color   
 'value.snap': ('SNAP', '#2B3514'),
 'value.schoolmeals': ('School Meals', '#D32B1E'),
 'value.section8': ('Section 8', '#6F340D'),
 'value.liheap': ('LIHEAP', '#92AE31'),
 'value.medicaid.adult': ('Medicaid (Adult)', '#7E1510'),
 'value.medicaid.child': ('Medicaid (Child)', '#9a9a00'),
 'value.aca': ('ACA', '#91218C'),
 'value.employerhealthcare': ('Employer Healthcare', '#E1A11A'),
 'value.CCDF': ('CCDF', '#463397'),
 'value.HeadStart': ('Head Start', '#DF8461'),
 'value.PreK': ('Pre-K', '#4277B6'),
 'value.cdctc.fed': ('CDCTC (Federal)', '#D485B2'),
 'value.cdctc.state': ('CDCTC (State)', '#5FA641'),
 'value.ctc.fed': ('CTC (Federal)', '#7F7E80'),
 'value.ctc.state': ('CTC (State)', '#C0BD7F'),
 'value.eitc.fed': ('EITC (Federal)', '#BA1C30'),
 'value.eitc.state': ('EITC (State)', '#96CDE6'),
 'value.eitc': ('EITC', '#DB6917'),
 'value.ctc': ('CTC', '#702C8C'),
 'value.cdctc': ('CDCTC', '#EBCE2B'),
 'value.ssdi': ('SSDI', '#1D1D1D'),
 'value.ssi': ('SSI', '#DDDDDD')
 
 }

def create_custom_ticks_labels() -> tuple:     
    ## TO DO: let customize salary ranges from parameters  
    ## Create custom ticks for yearly and hourly wages 
    custom_ticks = list(range(30000, 100001, 10000)) 
    hourly_wages = [utils.get_hourly_wage(x) for x in custom_ticks]

    custom_labels = [f"${x[0]:,}\n{x[1]}" for x in zip(custom_ticks, hourly_wages)]
    return custom_ticks, custom_labels



### ------------------------------------------------------------------------------ ###
### --- PLOTLY TEMPLATES & HELPERS --- ###

def plot_single_profile(df, after_tax=False, title=None): 

    x_var = 'AfterTaxIncome' if after_tax else 'income'

    ## -- Base plot, Net Resources -- ## 
    fig = px.line(df, x=x_var, y='NetResources', 
                color_discrete_sequence=[plotting.beneficiary_color_palette[2]], 
                title=title)
    fig.update_traces(mode='markers+lines')

    ## -- Benefits Programs  -- ## 


    for n, col in enumerate(df_benefits_filtered): 
        visibility = 'legendonly' if 'eitc' in col or 'section8' in col else True
        fig.add_trace(go.Scatter(x=df[x_var],y=df[col], mode='markers+lines', line=dict(color=plotting.benefits_palette[n]), name=col, visible=visibility))

    ## -- Calculate Derivative  -- ## 
    x,y = df[x_var], df['NetResources']
    derivative = np.gradient(y,x)
    derivative_scale = 10000
    # Plot Derivative (optional)
    # fig.add_trace(go.Scatter(x=x,y=derivative * derivative_scale, mode='markers+lines', line=dict(color="grey"), name=f'1st Derivative (* {derivative_scale})'))
    derivative_rel_minima = argrelextrema(derivative, np.less)[0]
    derivative_rel_minima = derivative_rel_minima[derivative_rel_minima > 0] 

    ## -- Find Cliff Points & Annotate  -- ## 
    df_benefits = df[[col for col in df.columns if 'value' in col and 'eitc' not in col]] # filter to benefits columns 
    df_benefits = df_benefits.loc[:, ((df_benefits != 0).any(axis=0) & (df_benefits == 0).any(axis=0))] # drop cols with only zero and no zero
    benefits_zeros = [{col:df_benefits[col].to_list().index(0)} for col in df_benefits.columns]
    benefits_zeros.sort(key=lambda x: list(x.values())[0])

    cliffs = [{"benefit":list(z.keys())[0],
                "valley":list(z.values())[0], 
                "peak":list(z.values())[0] - 1}
            for z in benefits_zeros 
            if any(list(z.values())[0] in pd.Interval(e-1,e+1)
                for e in derivative_rel_minima)]

    # Add annotation of the program which is lost 
    for cliff in cliffs:
        # print(cliff)
        income_level = x[cliff['peak']]
        income_level_str = '${:,.6}'.format(float(income_level)).rstrip('0').rstrip('.')
        resource_level = y[cliff['peak']]     

        fig.add_annotation(
            x=income_level,
            y=resource_level,
            xref="x",
            yref="y",
            text=f"{ben_display_map[cliff['benefit']]}<br>{income_level_str}",
            showarrow=True,
            font=dict(
                # family="Courier New, monospace",
                size=12,
                color="#ffffff"
                ),
            align="center",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#636363",
            ax=-40,
            ay= 40,
            bordercolor="#c7c7c7",
            borderwidth=2,
            borderpad=4,
            bgcolor=beneficiary_color_palette[2],
            opacity=0.8
            )

    ## --- Customizing Hover Text --- ## 


    ## -- Add baseline (break-even) -- ## 
    fig.add_shape(type="line",
                x0=df[x_var].min(),
                y0=0,
                x1=df[x_var].max(),
                y1=0,
                line=dict(color="red",width=4,dash="dash"),
                )

    ## --- Adding Legend(s) --- ## 

    # legend_text = f'<span style="{color_palette[2]}"><b>Family</b></span> <i>(Age, Disabled, Blind, Monthly SSDI)<br></i>'
    legend_text = f"<span style='color:{plotting.beneficiary_color_palette[2]};'><b>Family:</b></span> <i>(Age, Disabled, Blind, Monthly SSDI)<br></i>"

    legend_info = p2_child3.get_family()

    for fam_member, params in legend_info.items():
        legend_text = legend_text + f"<b>{fam_member}</b>: " 
        for v in params.values(): 
            legend_text += f"{v}, "
        legend_text = legend_text.rstrip(', ') + "<br>"
        
    ## Add Benefits List
    legend_text += "<i>" 
    ben_list = p2_child3.get_benefits()
    for i in range(len(ben_list)):
        if i % 3 == 0:
            legend_text += "<br>"
        legend_text += ben_list[i] + ", " 
    legend_text = legend_text.rstrip(",  ") + "</i>"


    fig.add_annotation(
        text=legend_text,
        align='left',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=1.4,
        y=0,

        bordercolor='black',
        borderwidth=1
    )

    # Update layout to adjust the legend position
    fig.update_layout(
        xaxis=dict(title=x_var),
        yaxis=dict(title=''),
        margin=dict(l=60, r=400, t=60, b=80), # margins for annotation
        height=600,
        width=1200

    )

    ## --- Customize Axis --- ## 
    fig.update_xaxes(labelalias={f"{n}k":f"${n},000 <br>(${(n * 1000) / (52 * 40):.2f}/hour)" for n in range(30, 80, 10)})
    # fig.update_yaxes(labelalias={f"{n}k":f"${n},000" for n in range(-15, 25, 5)})


    print([x for x in fig.select_yaxes()])

    ## --- Show Plot --- ## 

    fig.show()


def create_profile_legend_text(family_data:dict, ben_list:list, color): 
    """"""
    legend_text = f"<span style='color:{color};'><b>Family:</b></span> <i>(Age, Disabled, Blind, Monthly SSDI)<br></i>"

    for fam_member, params in family_data.items():
        legend_text = legend_text + f"<b>{fam_member}</b>: " 
        for v in params.values(): 
            legend_text += f"{v}, "
        legend_text = legend_text.rstrip(', ') + "<br>"
        
    ## Add Benefits List
    legend_text += "<i>" 
    for i in range(len(ben_list)):
        if i % 3 == 0:
            legend_text += "<br>"
        legend_text += ben_list[i] + ", " 
    legend_text = legend_text.rstrip(",  ") + "</i>"

    return legend_text



### ------------------------------------------------------------------------------ ###
### ---  MATPLOTLIB TEMPLATES & HELPERS --- ###

def plot_ben_cliff(x, y, 
                   label_curve, 
                   label_x='Income (Annual & Hourly)', 
                   label_y='Net Resources',
                   title='Net Resources'): 


    ## Create figure, axis, and plot data 
    fig, ax = plt.subplots()
    ax.plot(x,y, label=label_curve)

    ## Add break even line 
    plt.axhline(y=0, color='r', linestyle='--', label='Break Even')

    ## Add legend 
    plt.legend()

    ## Create custom ticks for yearly and hourly wages 
    # read from the current config file 
    custom_ticks = list(range(30000, 100001, 10000)) 
    def get_hourly_wage(x):
        # Assuming you work a 40 hour week, 52 weeks in a year 
        return f"${(x/52)/40:.2f}"
    hourly_wages = [get_hourly_wage(x) for x in custom_ticks]

    custom_labels = [f"${x[0]:,}\n{x[1]}" for x in zip(custom_ticks, hourly_wages)]

    ## Set custom ticks and labels for x axis 
    ax.set_xticks(custom_ticks)
    ax.set_xticklabels(custom_labels)

    ## Set axis labels and title
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    ax.set_title(title)

    ## Show plot 
    plt.show()