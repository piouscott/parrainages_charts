#!/usr/bin/env python
# coding: utf-8

# In[8]:


from flask import Flask, render_template, redirect, url_for, request
import pandas as pd
import json
import plotly
from plotly.subplots import make_subplots
import plotly.express as px
import requests
import plotly.graph_objects as go
import numpy as np
import os as os

app = Flask(__name__)

@app.route('/')
def index():    return render_template('index.html')

r = requests.get("https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.json")
decoded_data = r.text.encode().decode('utf-8-sig')
d = json.loads(decoded_data)


# In[34]:


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
mes_figues = []
for Candidat,group in pt_test_new_way.sort_values(by="Partdhommes",ascending=False).groupby(["Candidat"]):
    monsieur=group.query('Civilite=="M."')
    mme=group.query('Civilite=="Mme"')
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monsieur["transco_mandat"],
                y=monsieur['total_civi_mandat'],
                name='M.',
                marker_color='rgb(219, 165, 71)',
                width=1
                ,marker = dict(line = dict(width = 1,
                          color = 'rgb(0, 0, 0)'))
                )
                  )
    
    fig.add_trace(go.Bar(x=mme["transco_mandat"],
                y=mme['total_civi_mandat'],
                name='Mme',
                marker_color='rgb(43, 150, 195)',
                width=1
                         ,marker = dict(line = dict(width = 1,
                          color = 'rgb(0, 0, 0)'))
                )
                 )
    fig.add_trace(go.Scatter(x=group["transco_mandat"],
                             y=group["Partdhommes"], 
                             name="Hommes en fonction"))
    fig.update_layout(barmode='stack')
    fig.update_layout(barnorm='percent')
    fig.update_layout(showlegend=True)
    fig.update_layout(
        title_text=Candidat+"| Nombre total de parrainages:"+str(int(group["total_civi_mandat"].sum()))
    )
    fig.update_layout(
    autosize=False,
    width=500,
    height=500,
    margin=dict(
    l=50,
    r=50,
    b=100,
    t=100,
    pad=4)
    )
    fig.show()
    mes_figues.append(fig)


# In[35]:


# Création d'un seul fichier HTML
filename=f"{os.path.join('sortie', 'liste_complete.html')}"
dashboard = open(filename, 'w')
dashboard.write("<html><head></head><body>" + "\n")
include_plotlyjs = True

for fig in mes_figues:
    inner_html = fig.to_html(include_plotlyjs = include_plotlyjs).split('<body>')[1].split('</body>')[0]
    dashboard.write(inner_html)
    include_plotlyjs = False
dashboard.write("</body></html>" + "\n")

