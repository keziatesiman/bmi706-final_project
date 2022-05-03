import os
import zipfile
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from vega_datasets import data
from rdkit import Chem
from rdkit import rdBase
from rdkit.Chem import AllChem
from rdkit.Chem import DataStructs
from rdkit.Chem import PandasTools
from rdkit.Chem import RDConfig
from rdkit.Chem import Draw
from rdkit.Chem.Draw import IPythonConsole
 
from sklearn.decomposition import PCA

def mol2fparr(mol):
    arr = np.zeros((0,))
    #print(mol)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol,2)
    DataStructs.ConvertToNumpyArray(fp, arr)
    #except Exception: 
    #   pass
    return arr
    

@st.cache
def load_data():


    #Now, we can read in the data
    df = pd.read_csv('df_molecule_pca.csv')

    return df


def app():

    #country_code_df, df_merged_grouped, df_merged_grouped3 , df_country_new, SFbyCountry, success_count, fail_count = load_data()
    df  = load_data()

    st.write("## Visualizing Drug Molecules")
    
    chart1 = alt.Chart(df[0:5000]).mark_point().encode(
           x = 'PCA1',
           y = 'PCA2',
           color = 'block_desc',
           tooltip = ['nct_id', 'smiless_first']).interactive()
    
    #######
    st.altair_chart(chart1, use_container_width=True)
