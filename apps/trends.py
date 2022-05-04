import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from vega_datasets import data

@st.cache
def load_data():

    # Open compressed country data
    with zipfile.ZipFile("df_country.zip") as myzip:    
        country_df = myzip.open("df_country.csv") # Dataset containing country data (each row is a trial-country pair)
        
    # Read country data
    df = pd.read_csv(eval('country_df'))
    
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
    st.write("Sources: [ClinicalTrials.gov](https://clinicaltrials.gov/) via [AACT](https://aact.ctti-clinicaltrials.org/pipe_files) and [Trials Outcome Prediction](https://github.com/futianfan/clinical-trial-outcome-prediction)")
    
    st.write("## Global Trends")

    ### Select year ###
    year = st.slider("Year", 1999, 2020, 2012) # Range: 1999, 2012. Default: 2012
    # Subsetting df by year
    df = df[df["year"] <= year]

    ### Select information type: Radio button ###
    participant_or_trial = st.radio(
        "Display total: ",
        ('Trials', 'Participants')
    )

    # Trial count per country
    df_country_new = df.groupby(['country','country-code', 'year']).agg(trials_count=('nct_id', np.size)).reset_index()

    # Participant count per country
    df_country_participant= df.groupby(['country','country-code', 'year']).agg(participants_counts=('participant_count', np.sum)).reset_index()

    ### Global Trends Map ###
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

    timeline = alt.Chart(df_country_new).mark_line().encode(
        x=alt.X("year:O"),
        y=alt.Y("trials_count"),
        color="country"
    )

    st.altair_chart(timeline, use_container_width=True)

    # Display trial count data
    if participant_or_trial == 'Trials':
        base = alt.Chart(source
        ).properties( 
            width=width,
            height=height
        ).project(project
        ).transform_lookup(
            lookup="id",
            from_=alt.LookupData(df_country_new, "country-code", fields =['trials_count', 'country']),
        )

        rate_scale = alt.Scale(domain=[df_country_new['trials_count'].min(), df_country_new['trials_count'].max()])
        rate_color = alt.Color(field="trials_count", type="quantitative", scale=rate_scale)
        chart_rate = base.mark_geoshape().encode(
            color='trials_count:Q',
            tooltip=['trials_count:Q', 'country:N']
            )

    # Display participant data
    if participant_or_trial == 'Participants': 
        base = alt.Chart(source
        ).properties( 
            width=width,
            height=height
        ).project(project
        ).transform_lookup(
            lookup="id",
            from_=alt.LookupData(df_country_participant, "country-code", fields =['participants_counts', 'country']),
        )

        rate_scale = alt.Scale(domain=[df_country_participant['participants_counts'].min(), df_country_participant['participants_counts'].max()])
        rate_color = alt.Color(field="participants_counts", type="quantitative", scale=rate_scale)
        chart_rate = base.mark_geoshape().encode(
            color='participants_counts:Q',
            tooltip=['participants_counts:Q', 'country:N']
            )        


    st.altair_chart(background + chart_rate, use_container_width=True)
    



    '''
    ### select country ###

    st.write("## Trends Per Country")

    countries = ["Austria","Germany","Iceland","Spain","Sweden","Thailand","Turkey"]
    countries = st.multiselect("Countries", pd.unique(df_country_new["country"]), countries)
    subset = subset[subset["country"].isin(countries)]

    # subset of df_country_new
    df2 = subset.groupby(['country','country-code','year']).agg(trials_count=('nct_id', np.size)).reset_index()
    df2_1 = subset[subset["participant_count"].notna()]
    df2_1 = subset.groupby(['country','country-code','year']).agg(participant_count=('participant_count', np.sum)).reset_index()

    #subset of df_merged_grouped3
    df3 = subset.groupby(['outcome','phase']).agg(trials_count=('nct_id', np.size)).reset_index()

    ### bar chart ###

    chart3 = alt.Chart(df2).mark_bar().encode(
        x="country",
        y="sum(trials_count)",
        tooltip=["sum(trials_count)"]
    )

    chart3_1 = alt.Chart(df2_1).mark_bar().encode(
        x="country",
        y="sum(participant_count)",
        tooltip=["sum(participant_count)"],
        color=alt.value("orange")
    )

    ### line plot ###

    chart4 = alt.Chart(df2).mark_line().encode(
        x=alt.X("year:O"),
        y=alt.Y("trials_count"),
        color="country"
    )

    ### pie chart ###

    select_phase = alt.selection_single(fields=[alt.FieldName("phase")])

    chart5_left = alt.Chart(df3).mark_arc().encode(
        theta="sum(trials_count)",
        color="phase",
        opacity=alt.condition(select_phase, alt.value(1), alt.value(0.5)),
    ).add_selection(select_phase
    ).properties(
        width=250
    )

    chart5_right = alt.Chart(df3).mark_arc().encode(
        theta="trials_count",
        color="outcome:O",
    ).transform_filter(select_phase
    ).properties(
        width=250
    )

    chart5 = alt.hconcat(chart5_left, chart5_right
    ).resolve_scale(
        color="independent",
        theta="independent"
    )

    st.write("### Clinical Trials Per Country")
    st.altair_chart(chart3, use_container_width=True)

    st.write("### Participants Per Country")
    st.write("*For trials with participant data available")
    st.altair_chart(chart3_1, use_container_width=True)

    st.write("### Clinical Trials Over Time")
    st.altair_chart(chart4, use_container_width=True)

    st.write("### Success Rate Per Phase")
    st.altair_chart(chart5)
'''