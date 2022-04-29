import altair as alt
import pandas as pd
import streamlit as st
import os
import zipfile
import numpy as np 

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
    return df_merged_grouped


# Uncomment the next line when finished
# df = load_data()

### P1.2 ###
df_merged_grouped = load_data()

st.write("## Clinical Trials Visualization")


chart = alt.Chart(df_merged_grouped).mark_bar().encode(
    x='trials_count',
    y='phase',
    color='status'
)

st.altair_chart(chart, use_container_width=True)