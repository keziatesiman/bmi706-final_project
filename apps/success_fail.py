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
    df = country_code_d

    df_country_new = country_code_df.groupby(['country','country-code']).agg(trials_count=('nct_id', np.size)).reset_index()

    return df, df_merged_grouped, df_merged_grouped3, df_country_new


def app():

    country_code_df, df_merged_grouped, df_merged_grouped3 , df_country_new = load_data()
   


    st.write("## Visualizing Trial Success and Failure")
    st.write("## What happens at each phase?")

    chart1 = alt.Chart(df_merged_grouped).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='percentage')),
        y='phase',
        color='status'
    )
    
    st.write("## Sucesses and Failures by Phase")


    st.altair_chart(chart1, use_container_width=True)

