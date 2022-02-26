
        return redirect(url_for('chart2'))
    else:
        r = requests.get("https://presidentielle2022.conseil-constitutionnel.fr/telechargement/parrainagestotal.json")
        d = json.loads(r.text)
        """pt""" 
        pt = pd.DataFrame(d)
        tm = pd.read_csv('transco_mandat.csv')
        rf = pd.read_csv('repart_femme_ok.csv')
        query =""" SELECT count(*) as repart
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
                rf
            ON 
                tm.transco_mandat = rf.Mandat
		    WHERE 
                pt.Candidat like \"%form_candidat%"\
		    group by 
                tm.transco_mandat, pt.Candidat , pt.Civilite
            order by 
                tm.transco_mandat ASC"""
        df=(ps.sqldf(query, locals()))

        """fig = px.bar(y=df["pourcent_civi"],x=df["transco_mandat"],color=df["Civilite"],barmode="stack")"""
        """fig.add_scatter(x=rf["Mandat"], y=rf["Partdefemmes"], name="Femmes en fonction")"""
        fig = px.histogram(df, x="transco_mandat",y="pourcent_civi", color="Civilite")
        fig.add_scatter(x=df["rfmandat"],y=df["Partdhommes"], name="Hommes en fonction",mode="lines")

        """WORKING FIGURE
        fig = px.line(x=rf["Mandat"], y=rf["Partdefemmes"], color=px.Constant("Femmes en fonction"),
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

