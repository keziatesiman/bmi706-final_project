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

    subset = df[df['year'].notna()]
    year = st.slider("Year", 1999, 2020, 2012)
    subset = subset[subset["year"] <= year]

    countries = ["Austria","Germany","Iceland","Spain","Sweden","Thailand","Turkey"]
    countries = st.multiselect("Countries", pd.unique(df_country_new["country"]), countries)
    subset = subset[subset["country"].isin(countries)]

    df2 = subset.groupby(['country','country-code']).agg(trials_count=('nct_id', np.size)).reset_index()

    ### map ###

    source = alt.topo_feature(data.world_110m.url, 'countries')

    width = 900
    height  = 400
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
            from_=alt.LookupData(df_country_new, "country-code", fields =['trials_count', 'country']),
        )

    rate_scale = alt.Scale(domain=[df_country_new['trials_count'].min(), df_country_new['trials_count'].max()])
    rate_color = alt.Color(field="trials_count", type="quantitative", scale=rate_scale)
    chart_rate = base.mark_geoshape().encode(
        color='trials_count:Q',
        tooltip=['trials_count:Q', 'country:N']
        )
    
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

    st.write("## Clinical trials per country")
    st.altair_chart(background + chart_rate, use_container_width=True)
    st.altair_chart(chart3, use_container_width=True)
    st.altair_chart(chart4, use_container_width=True)
