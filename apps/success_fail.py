import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from vega_datasets import data
from altair import pipe, limit_rows, to_values

@st.cache
def load_data():

    with zipfile.ZipFile("df_country.zip") as myzip:    
        no1 = myzip.open("df_country.csv")
    with zipfile.ZipFile("df_inclusion_exclusion.zip") as myzip:    
        no2 = myzip.open("df_inclusion_exclusion.csv")

    #Now, we can read in the data
    df = pd.read_csv(eval('no1'))
    df2 = pd.read_csv(eval('no2'))
    

    df_merged_grouped = df.groupby(['phase','status']).agg(trials_count=('nct_id', lambda x: x.nunique())).reset_index()

    df_merged_grouped3 = df.groupby(['outcome','phase']).agg(trials_count=('nct_id', lambda x: x.nunique())).reset_index()
    
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

    SFbyPhase = country_code_df.groupby(['phase','outcome']).agg(trials_count=('nct_id', np.size)).reset_index()

    df = df[df['year'].notna()]
    df['year'] = df['year'].astype(int)
	

    df.loc[(df.participant_count < 10),  'participant_countGroup'] = '1-10'
    df.loc[(df.participant_count > 10),  'participant_countGroup'] = '11-25'
    df.loc[(df.participant_count > 50),  'participant_countGroup'] = '25-50'
    df.loc[(df.participant_count > 75),  'participant_countGroup'] = '75+'

    participant_countGroupDF = df.groupby(['participant_countGroup','outcome']).agg(trials_count=('nct_id', np.size)).reset_index()
	
    return df, df_merged_grouped, df_merged_grouped3, df_country_new, SFbyCountry, SFbyYear, participant_countGroupDF, SFbyPhase, df2 


def app():

    #country_code_df, df_merged_grouped, df_merged_grouped3 , df_country_new, SFbyCountry, success_count, fail_count = load_data()
    df, df_merged_grouped, df_merged_grouped3 , df_country_new, SFbyCountry, SFbyYear, participant_countGroupDF, SFbyPhase, df2 = load_data()
   


    st.write("## Visualizing Trial Success and Failure")
    st.write("## What happens at each phase?")

    chart1 = alt.Chart(df_merged_grouped).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='percentage')),
        y='phase',
        color='status',
        tooltip = ['sum(trials_count)', 'phase','status']
    )
    
    chart1B = alt.Chart(SFbyPhase).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='percentage')),
        y='phase',
        color=alt.Color('outcome'),
        tooltip = ['sum(trials_count)', 'phase','outcome:N']
    )
    
    ########

    chart2 = alt.Chart(SFbyCountry).mark_bar().encode(
        x=alt.X('sum(trials_count)', stack="normalize", axis=alt.Axis(format='%', title='Percentage')),
        y='country',
        color=alt.Color('outcome', legend=None),
        tooltip = ['sum(trials_count)', 'country','outcome']
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
        color=alt.Color('outcome', legend=None),
        tooltip = ['sum(trials_count)','year','outcome']
    )
 #######
    
    chart5 = alt.Chart(participant_countGroupDF).mark_bar().encode(
        x=alt.X('participant_countGroup', axis=alt.Axis(title='Number of Patients')),
        y=alt.X('trials_count:Q',stack="normalize", axis=alt.Axis(format='%', title='Success/Failure %')),
        color=alt.Color('outcome', legend=None),
        tooltip = ['participant_countGroup','trials_count','outcome']
    )
####### 
    
    brush = alt.selection(type='interval', resolve='global')

    base_criteria = alt.Chart(df2[df2.phase =='phase 3']).mark_circle().encode(
        alt.Y("participant_count:Q", title="Number of Patients"),
        tooltip = ['nct_id','inclusion','exclusion','participant_count','status'],
        color=alt.condition(
            brush, 
            'outcome:N', 
            alt.ColorValue('gray')
            )
        ).add_selection(
                brush
        )
    
    chart_inclusion = base_criteria.encode(
        alt.X("inclusion:Q", title='Number of Inclusion Criteria')
        )
    
    chart_exclusion = base_criteria.encode(
        alt.X("exclusion:Q", title='Number of Exclusion Criteria'))
    

        #######
    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart1B, use_container_width=True)
    st.write("## Where do trials fail?")
    st.altair_chart(chart2, use_container_width=True)
    st.write("## Trends Over Time")
    st.altair_chart(chart4, use_container_width=True)
    st.write("## Does size matter?")
    st.altair_chart(chart5, use_container_width=True)

    st.write("## Does the number of inclusion / exclusion criteria matter?")
    st.altair_chart(chart_inclusion | chart_exclusion, use_container_width=True)

    st.write("## Does trial success depend on the therapeutic area and year?")
    

    phase_option = pd.unique(df['phase']).tolist()
    phase = st.selectbox(
        'Phase',
        phase_option)

    chart7 = alt.Chart(df[df.phase ==phase]).mark_circle().encode(
        alt.X('year(study_date):T', scale=alt.Scale(zero=False), title = 'Year'),
        alt.Y('block_desc:N', scale=alt.Scale(zero=False, padding=1), title = 'Disease class'),
        color='outcome:N',
        size='participant_count:Q'
        ,tooltip=['nct_id','participant_count','status','phase','diseases','drugs','outcome']
    )
#########


    st.altair_chart(chart7, use_container_width=True)

 #######


'''
    base = alt.Chart(df[df.phase ==phase]).mark_circle(color="red").encode(
        alt.X("probability_success"), alt.Y("participant_count"),tooltip=['probability_success','participant_count']
    )
    base.encoding.x.title = 'Historical Success Rate'
    base.encoding.y.title = 'Number of Patients'

    chart6 = base+ base.transform_regression('probability_success', 'participant_count').mark_line()


    ### Remove chart 6
    st.write("## Correlation between number of patients and historical success rate")
    st.altair_chart(chart6, use_container_width=True)
'''

#########
    