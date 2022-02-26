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
    r = requests.get("https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.json")
    d = json.loads(r.text)
    pt = pd.DataFrame(d)
    tm = pd.read_csv('transco_mandat.csv')
    rf = pd.read_csv('repart_femme_ok.csv')
    
    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")






    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Fruit in North America"
    description = """
    A academic study of the number of apples, oranges and bananas in the cities of
    San Francisco and Montreal would probably not come up with this chart.
    """
    return render_template('notdash2.html', graphJSON=graphJSON, header=header,description=description)


