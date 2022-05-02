import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from vega_datasets import data

@st.cache
def load_data():

    with zipfile.ZipFile("smaller.zip") as myzip:    
        no1 = myzip.open("smaller.csv")

    #Now, we can read in the data
    df = pd.read_csv(eval('no1'))

    df_merged_grouped = df.groupby(['phase','status']).agg(trials_count=('nct_id', np.size)).reset_index()

    df_merged_grouped3 = df.groupby(['outcome','phase']).agg(trials_count=('nct_id', np.size)).reset_index()
    
    country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'country-code': str})
    country_df = country_df[['Country', 'country-code']]
    country_df = country_df.replace('United States of America', 'United States')

    country_code_df = pd.merge(df, country_df,  how='left', left_on='country', right_on='Country')
    country_code_df["year"] = pd.DatetimeIndex(country_code_df["study_date"]).year.astype("float")
    df = country_code_df

    df_country_new = country_code_df.groupby(['country','country-code']).agg(trials_count=('nct_id', np.size)).reset_index()
    
    SFbyCountry = country_code_df.groupby(['country','country-code','outcome']).agg(trials_count=('nct_id', np.size)).reset_index()
    
    countries = ["Austria","Germany","Iceland","Spain","Sweden","Thailand","Turkey"]
    SFbyCountry = SFbyCountry[SFbyCountry["country"].isin(countries)]
    
    
    return df, df_merged_grouped, df_merged_grouped3, df_country_new, SFbyCountry


def app():

    country_code_df, df_merged_grouped, df_merged_grouped3 , df_country_new, SFbyCountry = load_data()
   


    st.write("## Visualizing Trial Success and Failure")
    st.write("## What happens at each phase?")

    chart1 = alt.Chart(df_merged_grouped).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='percentage')),
        y='phase',
        color='status'
    )
    
    
    ########
    st.write("## Sucesses and Failures by Phase")
    
    chart2 = alt.Chart(SFbyCountry).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='percentage')),
        y='country',
        color='outcome'
    )


    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart2, use_container_width=True)
