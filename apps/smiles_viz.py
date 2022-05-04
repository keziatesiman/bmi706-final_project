import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from vega_datasets import data


@st.cache
def load_data():


    #Now, we can read in the data
    df = pd.read_csv('df_molecule_pca.csv')
    df = df.rename(columns={'block_desc':'Disease group'})

    return df


def app():

    #country_code_df, df_merged_grouped, df_merged_grouped3 , df_country_new, SFbyCountry, success_count, fail_count = load_data()
    df  = load_data()

    st.write("## Visualizing Drug Molecule Structure with PCA")
    
    chart1 = alt.Chart(df[0:5000]).mark_point().encode(
           x = 'PCA1',
           y = 'PCA2',
           color = 'Disease group',
           tooltip = ['nct_id', 'smiless_first']).interactive()
    
    #######
    st.altair_chart(chart1, use_container_width=True)
