import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from vega_datasets import data

@st.cache
def load_data():

    with zipfile.ZipFile("full_df.zip") as myzip:    
        no1 = myzip.open("full_df.csv")

    #Now, we can read in the data
    df = pd.read_csv(eval('no1'))

    ####	
    df = df.head(100000)
    
    #####
    
    #success_count = df[df.outcome == 1]
    #success_count = success_count[success_count.participant_count  > 0]
    
    #fail_count = df[df.outcome == 0]
    #fail_count = fail_count[fail_count.participant_count  > 0]
    
    ####

    df_merged_grouped = df.groupby(['phase','status']).agg(trials_count=('nct_id', np.size)).reset_index()

    df_merged_grouped3 = df.groupby(['outcome','phase']).agg(trials_count=('nct_id', np.size)).reset_index()
    
    country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'country-code': str})
    country_df = country_df[['Country', 'country-code']]
    country_df = country_df.replace('United States of America', 'United States')

    country_code_df = pd.merge(df, country_df,  how='left', left_on='country', right_on='Country')
    country_code_df["year"] = pd.DatetimeIndex(country_code_df["study_date"]).year.astype("float")
    df = country_code_df

    df_country_new = country_code_df.groupby(['country','country-code']).agg(trials_count=('nct_id', np.size)).reset_index()
    ###
    SFbyCountry = country_code_df.groupby(['country','country-code','outcome']).agg(trials_count=('nct_id', np.size)).reset_index()
    
    countries = ["Austria","Germany","Iceland","Spain","Sweden","Thailand","Turkey"]
    SFbyCountry = SFbyCountry[SFbyCountry["country"].isin(countries)]

    ###
	
    SFbyYear = country_code_df.groupby(['year','outcome']).agg(trials_count=('nct_id', np.size)).reset_index()
        
    #return df, df_merged_grouped, df_merged_grouped3, df_country_new, SFbyCountry, success_count, fail_count

    ####

    df = df[df['year'].notna()]
    df['year'] = df['year'].astype(int)
	
    ####

    df.loc[(df.participant_count < 50),  'participant_countGroup'] = '1-25'
    df.loc[(df.participant_count > 25),  'participant_countGroup'] = '26-50'
    df.loc[(df.participant_count > 50),  'participant_countGroup'] = '51-100'
    df.loc[(df.participant_count > 100),  'participant_countGroup'] = '100+'

    participant_countGroupDF = df.groupby(['participant_countGroup','outcome']).agg(trials_count=('nct_id', np.size)).reset_index()
	
    df['outcome'] = df['outcome'].map({'Success': 1, 'Failure': 0})

    return df, df_merged_grouped, df_merged_grouped3, df_country_new, SFbyCountry, SFbyYear, participant_countGroupDF


def app():

    #country_code_df, df_merged_grouped, df_merged_grouped3 , df_country_new, SFbyCountry, success_count, fail_count = load_data()
    country_code_df, df_merged_grouped, df_merged_grouped3 , df_country_new, SFbyCountry, SFbyYear, participant_countGroupDF = load_data()
   


    st.write("## Visualizing Trial Success and Failure")
    st.write("## What happens at each phase?")

    chart1 = alt.Chart(df_merged_grouped).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='percentage')),
        y='phase',
        color='status'
    )
    
    
    ########

    chart2 = alt.Chart(SFbyCountry).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='Percentage')),
        y='country',
        color=alt.Color('outcome')
    )

    
    
    ########

    #country_code_df = country_code_df[country_code_df['participant_count'].notna()]
	
    #successCount = country_code_df[country_code_df.outcome == 1]
    #failCount = country_code_df[country_code_df.outcome == 0]

    #chart3 = alt.Chart(country_code_df).mark_bar().encode(
    #    alt.X("participant_count:Q", bin=True),
    #    y='count()',
    #)

    #chart3 = alt.Chart(country_code_df).mark_bar().encode(
    #x='participant_count:O',
    #y='sum(yield):Q',
    #color='outcome:N',
    #column='outcome:N'
#)

	

    chart4 = alt.Chart(SFbyYear).mark_bar().encode(
        y=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='Success/Failure %')),
        x='year',
        color=alt.Color('outcome', legend=None)
    )
 #######
	
    chart5 = alt.Chart(participant_countGroupDF).mark_bar().encode(
        x=alt.X('participant_countGroup', axis=alt.Axis(title='Number of Subjects')),
        y=alt.X('trials_count:Q',stack="normalize", axis=alt.Axis(format='%', title='Success/Failure %')),
        color=alt.Color('outcome', legend=None)
    )
    
    #######
    st.altair_chart(chart1, use_container_width=True)
    st.write("## Where do trials fail?")
    st.altair_chart(chart2, use_container_width=True)
    st.write("## Trends Over Time")
    st.altair_chart(chart4, use_container_width=True)
    st.write("## Does size Matter?")
    st.altair_chart(chart5, use_container_width=True)
