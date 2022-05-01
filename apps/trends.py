import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from vega_datasets import data

@st.cache
def load_data():

    with zipfile.ZipFile("merged_datasets.zip") as myzip:    
        no1 = myzip.open("merged_datasets/phase_I_test.csv")
        no2 = myzip.open("merged_datasets/phase_I_valid.csv")
        no3 = myzip.open("merged_datasets/phase_I_train.csv")
        no4 = myzip.open("merged_datasets/phase_II_valid.csv")
        no5 = myzip.open("merged_datasets/phase_II_test.csv")
        no6 = myzip.open("merged_datasets/phase_II_train.csv")
        no7 = myzip.open("merged_datasets/phase_III_valid.csv")
        no8 = myzip.open("merged_datasets/phase_III_test.csv")
        no9 = myzip.open("merged_datasets/phase_III_train.csv")
        
    #Now, we can read in the data
    df = pd.read_csv(eval('no1'))

    for i in range(2,10): 
        df_temp = pd.read_csv(eval('no'+ str(i)))
        df = df.append(df_temp, ignore_index=True)

    df_merged_grouped = df.groupby(['phase','status']).agg(trials_count=('nct_id', np.size)).reset_index()

    df_merged_grouped3 = df.groupby(['outcome','phase']).agg(trials_count=('nct_id', np.size)).reset_index()
    
    country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'country-code': str})
    country_df = country_df[['Country', 'country-code']]
    country_df = country_df.replace('United States of America', 'United States')

    country_code_df = pd.merge(df, country_df,  how='left', left_on='country', right_on='Country')
    country_code_df["year"] = pd.DatetimeIndex(country_code_df["study_date"]).year.astype("float")
    df = country_code_df

    df_country_new = country_code_df.groupby(['country','country-code']).agg(trials_count=('nct_id', np.size)).reset_index()

    return df, df_merged_grouped, df_merged_grouped3, df_country_new


def app():

    df, df_merged_grouped, df_merged_grouped3 , df_country_new = load_data()

    st.write("# Visualizing Trends in Clinical Trials")
    st.write("## Global trends")

    ### select year ###

    subset = df[df['year'].notna()]
    year = st.slider("Year", 1999, 2020, 2012)
    subset = subset[subset["year"] <= year]

    # subset of df_country_new
    df2 = subset.groupby(['country','country-code','year']).agg(trials_count=('nct_id', np.size)).reset_index()

    ### map ###

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

    base = alt.Chart(source
        ).properties( 
            width=width,
            height=height
        ).project(project
        ).transform_lookup(
            lookup="id",
            from_=alt.LookupData(df2, "country-code", fields =['trials_count', 'country']),
        )

    rate_scale = alt.Scale(domain=[df2['trials_count'].min(), df2['trials_count'].max()])
    rate_color = alt.Color(field="trials_count", type="quantitative", scale=rate_scale)
    chart_rate = base.mark_geoshape().encode(
        color='trials_count:Q',
        tooltip=['trials_count:Q', 'country:N']
        )

    st.altair_chart(background + chart_rate, use_container_width=True)
    
    ### select country ###

    st.write("## Trends per country")

    countries = ["Austria","Germany","Iceland","Spain","Sweden","Thailand","Turkey"]
    countries = st.multiselect("Countries", pd.unique(df_country_new["country"]), countries)
    subset = subset[subset["country"].isin(countries)]

    # subset of df_country_new
    df2 = subset.groupby(['country','country-code','year']).agg(trials_count=('nct_id', np.size)).reset_index()

    #subset of df_merged_grouped3
    df3 = subset.groupby(['outcome','phase']).agg(trials_count=('nct_id', np.size)).reset_index()

    ### bar chart ###

    chart3 = alt.Chart(df2).mark_bar().encode(
        x="country",
        y="trials_count",
        tooltip=["trials_count"]
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

    st.write("### Clinical trials per country")
    st.altair_chart(chart3, use_container_width=True)

    st.write("### Clinical trials over time")
    st.altair_chart(chart4, use_container_width=True)

    st.write("### Success rate per phase")
    st.altair_chart(chart5)