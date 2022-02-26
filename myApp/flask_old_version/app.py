from flask import Flask, render_template, redirect, url_for, request
import pandas as pd
import json
import plotly
from plotly.subplots import make_subplots
import plotly.express as px
import requests
import pandasql as ps
import plotly.graph_objects as go
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():    return render_template('index.html')

r = requests.get("https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.json")
d = json.loads(r.text)

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
    #chargement des fichiers dans les dataframes
    pt_origin = pd.DataFrame(d)
    rf = pd.read_csv('repart_femme_ok.csv')
    transco = pd.read_csv('transco_mandat.csv')
    #merge trasnco mandat et femmes repartition
    pt_test_new_way = pd.merge(pt_origin,transco,how='left', on=['Mandat'])
    pt_test_new_way.rename(columns={"Mandat": "oldMandat"})
    #remplacer les null par des 0
    pt_test_new_way= pt_test_new_way.fillna(0)
    pt_test_new_way = pd.merge(pt_test_new_way,rf,how='left', left_on=['transco_mandat'],right_on=['Mandat'])
    pt_test_new_way= pt_test_new_way.fillna(np.NaN)
    #on supprime la colonne date de publication
    pt_test_new_way = pt_test_new_way.drop('DatePublication',axis = 1)
    #on ajoute une colonne avec le count/civ/mandat
    group_civi_mandat = pt_test_new_way.groupby(["Candidat","transco_mandat","Civilite"]).agg(total_civi_mandat = ('Nom','count'))
    pt_test_new_way = pt_test_new_way.join(group_civi_mandat['total_civi_mandat'],how='left',on=["Candidat","transco_mandat","Civilite"])
    #on selectionne les colonnes voulues
    pt_test_new_way = pt_test_new_way[["Candidat","Civilite","total_civi_mandat","transco_mandat","Partdhommes"]]
    #on supprime les doublons
    pt_test_new_way = pt_test_new_way.drop_duplicates(subset = ["Candidat","Civilite","total_civi_mandat","transco_mandat","Partdhommes"])

    for Candidat,group in pt_test_new_way.sort_values(by="Partdhommes",ascending=False).groupby(["Candidat"]):
        monsieur=group.query('Civilite=="M."')
        mme=group.query('Civilite=="Mme"')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monsieur["transco_mandat"],
                    y=monsieur['total_civi_mandat'],
                    name='M',
                    marker_color='rgb(55, 83, 109)'
                    ))
        
        fig.add_trace(go.Bar(x=mme["transco_mandat"],
                    y=mme['total_civi_mandat'],
                    name='Mme',
                    marker_color='rgb(10, 35, 180)'
                    ))
        fig.add_trace(go.Scatter(x=group["transco_mandat"],
                                 y=group["Partdhommes"], 
                                 name="Hommes en fonction"))
        fig.update_layout(barmode='stack')
        fig.update_layout(barnorm='percent')
        fig.update_layout(showlegend=True)
        fig.update_layout(
            title_text=Candidat+"| Nombre total de parrainages:"+str(int(group["total_civi_mandat"].sum()))
        )

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        header="Répartition H/F et comparaison avec la réalité"
        description = """
        entrerdescription ici.
            """   
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)


    
