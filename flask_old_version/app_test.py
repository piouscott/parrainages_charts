from flask import Flask, render_template, redirect, url_for, request
import pandas as pd
import json
import plotly
from plotly.subplots import make_subplots
import plotly.express as px
import requests
import pandasql as ps
import plotly.graph_objects as go

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chart1')
def chart1():
    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Fruit in North America"
    description = """
    A academic study of the number of apples, oranges and bananas in the cities of
    San Francisco and Montreal would probably not come up with this chart.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)
""", methods=['GET','POST']"""
@app.route('/chart2')
def chart2():
    """ if request.method == 'POST':
    form_candidat = request.form.get("candidat")"""
    r = requests.get("https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.json")
    d = json.loads(r.text)
    """pt""" 
    pt = pd.DataFrame(d)
    tm = pd.read_csv('transco_mandat.csv')
    rf = pd.read_csv('repart_femme_ok.csv')
    query =""" SELECT 
                totals
                ,count(*) as repart
                ,rf.Mandat as rfmandat
                ,Partdhommes
               , tm.transco_mandat, pt.Candidat ,pt.Civilite
               ,round((round(count(*)*100,2)/group_civi_mandat),2) as pourcent_civi
               ,CASE
	               WHEN pt.Civilite = "Mme" and rf.Partdefemmes is not null THEN rf.Partdefemmes
	               WHEN pt.Civilite = "Mme" and rf.Partdefemmes is null THEN 0
	               WHEN pt.Civilite = "M." and rf.Partdefemmes is not null THEN (100-rf.Partdefemmes)
	               WHEN pt.Civilite = "M." and rf.Partdefemmes is null THEN 0
                   	end as repart_glob
                FROM pt left join tm on pt.mandat = tm.mandat
                LEFT JOIN 
	            (
	                SELECT
		                count(*) as group_civi_mandat
		                ,prt.Candidat
		                ,tsm.transco_mandat
	                FROM
		                pt prt
	                INNER JOIN
		                tm as tsm
	                ON 
		                prt.mandat = tsm.mandat
	                GROUP BY
		                prt.Candidat
		                ,tsm.transco_mandat
	            ) as tot_mandat
                ON 
                    pt.Candidat = tot_mandat.Candidat
                AND 
                    tm.transco_mandat = tot_mandat.transco_mandat
                LEFT JOIN
	            (
                    SELECT
	                    count(*) as totals
	                    ,Candidat
                    FROM
	                    pt
                    Group by 
	                    Candidat
                    Having 
	                    count(*)>400
	            ) as tot
                ON 
	                pt.Candidat = tot.Candidat
                LEFT JOIN 
                    rf
                ON 
                    tm.transco_mandat = rf.Mandat
	            WHERE 
                    totals > 400
                --    pt.Candidat like "%ARTHAUD%" or pt.Candidat like "%ZEMMOUR%"or pt.Candidat like "%LENCH%"
	            group by 
                    tm.transco_mandat, pt.Candidat , pt.Civilite
                order by 
                     pt.Candidat,tm.transco_mandat ASC"""
    df=(ps.sqldf(query, locals()))
    """@form_candidat"""
    """fig = px.bar(y=df["pourcent_civi"],x=df["transco_mandat"],color=df["Civilite"],barmode="stack")"""
    """fig.add_scatter(x=rf["Mandat"], y=rf["Partdefemmes"], name="Femmes en fonction")"""
    divide = int(df["Candidat"].nunique()/2)
    selected_list = df.Candidat.unique()
    print(selected_list)
    fig = make_subplots(rows=divide+1, cols=2,vertical_spacing = 0.20
        ,subplot_titles= selected_list)
    #,specs=[[{"secondary_y": True}, {"secondary_y": True}],
    #            [{"secondary_y": True}, {"secondary_y": True}]]
    #    )
    # Top left
    row = 1
    col = 1
    for Candidat,group2 in df.groupby("Candidat"):
    #    description = Candidat
        print(row)
        print(col)
        for Civilite, group in group2.groupby("Civilite"):
                fig.add_trace(
                    go.Bar(x=group["transco_mandat"], y=group["pourcent_civi"], name=Civilite),
                    row=row, col=col, secondary_y=False,)
            fig.update_layout(barmode='stack')
            fig.add_trace(
                go.Scatter(x=group["transco_mandat"],y=group["Partdhommes"], name="Hommes en fonction"),
                row=row, col=col, secondary_y=False,)
        #i = i + 1
        if (col == 1):
            col = col+1
        else:
            col = col-1
            row = row + 1
    fig.update_layout(
        autosize=False,
        width=1920,
        height=1080,
        margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
    paper_bgcolor="LightSteelBlue",
    )
    """
    for contestant, group in df.groupby("Contestant"):
        fig.add_trace(go.Bar(x=group["Fruit"], y=group["Number Eaten"], name=contestant,
        hovertemplate="Contestant=%s<br>Fruit=%%{x}<br>Number Eaten=%%{y}<extra></extra>"% contestant))
        fig.update_layout(legend_title_text = "Contestant")
        fig.update_xaxes(title_text="Fruit")
        fig.update_yaxes(title_text="Number Eaten")   
    # Top right
    fig.add_trace(
        go.Scatter(x=[1, 2, 3], y=[2, 52, 62], name="yaxis3 data"),
        row=1, col=2, secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis4 data"),
        row=1, col=2, secondary_y=True,
    )
    fig = px.histogram(df, x="transco_mandat",y="pourcent_civi", color="Civilite")
    fig.add_scatter(x=df["rfmandat"],y=df["Partdhommes"], name="Hommes en fonction",mode="lines")
    """
    """WORKING FIGURE"""
    """fig = px.line(x=rf["Mandat"], y=rf["Partdefemmes"], color=px.Constant("Femmes en fonction"),
             labels=dict(x="Mandat", y="PartH-F", color="Civilite"))
    fig.add_scatter(x=rf["Mandat"],y=rf["Partdhommes"], name="Hommes en fonction",mode="lines")
    fig.add_bar(y=df["pourcent_civi"], x=df["transco_mandat"],marker=dict(color="lightblue"))"""
    

    """fig = px.bar(df,y="pourcent_civi",x="transco_mandat",color="Civilite",barmode="group")"""
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Vegetables in Europe"
    description = """
    The rumor that vegetarians are having a hard time in London and Madrid can probably not be
    explained by this chart.
        """   
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)


    
