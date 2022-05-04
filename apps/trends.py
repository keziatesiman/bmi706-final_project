import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
from altair import datum
import streamlit as st
from vega_datasets import data

@st.cache
def load_data():

    # Open compressed country data
    with zipfile.ZipFile("df_country.zip") as myzip:    
        country_df = myzip.open("df_country.csv") # Dataset containing country data (each row is a trial-country pair)
        
    # Read country data
    df = pd.read_csv(eval('country_df'), index_col=0)
    
    # Loading country code data, to be used for mapping to world map
    country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'country-code': str})
    country_df = country_df[['Country', 'country-code']]
    country_df = country_df.replace('United States of America', 'United States')

    # Merge country code to main df
    df = pd.merge(df, country_df,  how='left', left_on='country', right_on='Country')
    
    # Store year data in datetime
    df["year"] = pd.DatetimeIndex(df["study_date"]).year.astype("float")

    return df


def app():

    df = load_data()

    # Page header
    st.write("# Visualizing Trends in Clinical Trials")
    st.write("A data visualization project by Kezia Irene, Manqing Liang, Nate Greenbaum and Nina Xiong.")
    st.write("Data sources: [ClinicalTrials.gov](https://clinicaltrials.gov/) via [AACT](https://aact.ctti-clinicaltrials.org/pipe_files) and [Trials Outcome Prediction](https://github.com/futianfan/clinical-trial-outcome-prediction)")
    
    st.write("## Clinical Trials thoughout the Years")

    ### Generating aggregated tables
    df_trial_count_year_country = df.groupby(['country','country-code','year','block_desc']).agg(trials_count=('nct_id', np.size)).reset_index() # Trial count per year per country per disease class

    ### 1. Timeline

    timeline = alt.Chart(df_trial_count_year_country).mark_bar().encode(
        x=alt.X("year:O"),
        y=alt.Y("sum(trials_count):Q"), # Sum of trials per year
        tooltip=['year:O', 'sum(trials_count):Q']
    ).properties(
        height=180
    )
    st.altair_chart(timeline, use_container_width=True)
    
    st.write("## Global Trends")

    ### 2. Geographical Trends ###

    ## Select year ###
    year = st.slider("Select a year", 1999, 2020, 2012) # Range: 1999, 2020. Default: 2012
    df_world_map = df_trial_count_year_country[df_trial_count_year_country["year"] <= year]

    ## Select a disease class ###
    diseases = ['Neoplasms']
    disease_class = st.multiselect("Disease class: ", pd.unique(df_world_map["block_desc"]), diseases)
    df_world_map = df_world_map[df_world_map["block_desc"].isin(disease_class)]

    # Background
    source = alt.topo_feature(data.world_110m.url, 'countries')
    width = 800
    height  = 450
    project = 'equirectangular'
    background = alt.Chart(source
    ).mark_geoshape(
        fill='#aaa',
        stroke='white'
    ).properties(
        width=width,
        height=height,
    ).project(project)

    # Base World Map
    base = alt.Chart(source
    ).properties( 
        width=width,
        height=height
        ).project(project
        ).transform_lookup(
            lookup="id",
            from_=alt.LookupData(df_world_map, "country-code", fields =['trials_count', 'country', 'disease_class','year']),
        )

    # Map values
    rate_scale = alt.Scale(domain=[df_world_map['trials_count'].min(), df_world_map['trials_count'].max()])
    rate_color = alt.Color(field='trials_count', type="quantitative", scale=rate_scale)
    chart_rate = base.mark_geoshape().encode(
        color='trials_count:Q',
        tooltip=['trials_count:Q', 'country:N']
        )
    
    st.altair_chart(background + chart_rate, use_container_width=True)   

    ### Present tabular data for further analysis
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    filtered_df = df[(df['year'] == year) & (df['block_desc'].isin(disease_class))][['nct_id','study_date','country','drugs','description','icdcodes_first','block_desc','status','phase','participant_count','outcome']]
    filtered_df = filtered_df.rename(columns = {'description': 'disease', 'icdcodes_first' : 'icd', 'block_desc': 'disease_class', 'outcome':'trial_outcome'})

    st.dataframe(filtered_df)

    csv = convert_df(filtered_df)

    st.download_button(
        "Press to Download",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv'
    )


    st.write("## Trends Per Country")

    countries = ["Austria","Germany","Iceland","Spain","Sweden","Thailand","Turkey"]
    countries = st.multiselect("Countries", pd.unique(df_trial_count_year_country["country"]), countries)
    subset = df_trial_count_year_country[df_trial_count_year_country["country"].isin(countries)]
    subset = subset[subset["year"]<= year]
    chart4 = alt.Chart(subset).mark_line().encode(
        x=alt.X("year:O"),
        y=alt.Y("trials_count:Q"),
        color="country",
        tooltip = ['year','trials_count', 'country']
    ).properties(
        width=400,
        height=250
        )
    st.altair_chart(chart4, use_container_width=True)

    df_new = df[df["country"].isin(countries)]
    df_new = df_new[df_new["year"]<= 2012]

    df3 = df_new.groupby(['outcome','phase']).agg(trials_count=('nct_id', np.size)).reset_index()
    select_phase = alt.selection_single(fields=[alt.FieldName("phase")])
    chart5_left = alt.Chart(df3).mark_bar().encode(
        x="phase",
        y="sum(trials_count)",
        opacity=alt.condition(select_phase, alt.value(1), alt.value(0.5)),
    ).add_selection(select_phase
    ).properties(
        width=250
    )

    chart5_right = alt.Chart(df3).mark_bar().encode(
        x="outcome:O",
        y="trials_count",
    ).transform_filter(select_phase
    ).properties(
        width=250
    )

    chart5 = alt.hconcat(chart5_left, chart5_right
    ).resolve_scale(
        x="independent",
        y="independent"
    )
    st.write("### Success Rate Per Phase")
    st.altair_chart(chart5)

