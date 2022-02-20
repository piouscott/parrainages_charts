from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px
import requests
import pandasql as ps

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

@app.route('/chart2')
def chart2():
    r = requests.get("https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.json")
    d = json.loads(r.text)
    """pt""" 
    pt = pd.DataFrame(d)
    tm = pd.read_csv('transco_mandat.csv')
    rf = pd.read_csv('repart_femme_ok.csv')
    query =""" SELECT count(*) as repart
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
                ON pt.Candidat = tot_mandat.Candidat
                AND tm.transco_mandat = tot_mandat.transco_mandat
                
                LEFT JOIN rf
                ON tm.transco_mandat = rf.Mandat
		
                WHERE pt.Candidat like "ZEMMOUR%"
		group by 
		tm.transco_mandat, pt.Candidat , pt.Civilite"""
    df=(ps.sqldf(query, locals()))
    """df = pd.DataFrame({
        "Vegetables": ["Lettuce", "Cauliflower", "Carrots", "Lettuce", "Cauliflower", "Carrots"],
        "Amount": [10, 15, 8, 5, 14, 25],
        "City": ["London", "London", "London", "Madrid", "Madrid", "Madrid"]
    })"""
    """fig = px.bar(y=df["pourcent_civi"],x=df["transco_mandat"],color=df["Civilite"],barmode="stack")"""
    """fig.add_scatter(x=rf["Mandat"], y=rf["Partdefemmes"], name="Femmes en fonction")"""
    fig = px.line(x=rf["Mandat"], y=rf["Partdefemmes"], color=px.Constant("Femmes en fonction"),
             labels=dict(x="Mandat", y="PartH-F", color="Civilite"))
    fig.add_scatter(x=rf["Mandat"],y=rf["Partdhommes"], name="Hommes en fonction",mode="lines")
    fig.add_bar(y=df["pourcent_civi"], x=df["transco_mandat"],marker=dict(color="lightblue"))
    """fig = px.bar(df,y="pourcent_civi",x="transco_mandat",color="Civilite",barmode="group")"""
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Vegetables in Europe"
    description = """
    The rumor that vegetarians are having a hard time in London and Madrid can probably not be
    explained by this chart.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)


    
