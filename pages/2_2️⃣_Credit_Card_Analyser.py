# Spend Analyser

# Import Libraries
import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from datetime import datetime
import calendar


# Page Settings
st.set_page_config(page_title='Spend Analyser',page_icon=':smile:',layout="wide")

url_saving='https://drive.google.com/uc?export=download&id=1IINDYx3LOWVe-Kjv-8ohFksvPHw_87h8'
url_credit='https://drive.google.com/uc?export=download&id=1XWcrAQzwxNYHpKRMoFAp91GBTEaWgxb7'

# CSS
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Helper functions
def tag(i):
    if 'ZOMATO' in i:
        return 'Zomato'
    elif 'SWIGGY' in i:
        return 'Swiggy'
    elif 'ATM-CASH' in i:
        return 'Cash Withdrawl'
    elif 'Jio' in i:
        return 'Jio Recharge'
    elif 'ASTAR' in i:
        return 'Salary Credited'
    elif 'PARVEEN' in i or 'Parvee' in i or 'Parveen' in i:
        return 'Sent to Parveen'
    elif 'Dish' in i:
        return 'Dishtv Recharge'
    elif 'CreditCard' in i:
        return 'Credit Card Payment'
    elif 'Dominos' in i:
        return 'Dominos'
    else :
        try:
            return i.split(',')[0]
        except:
            return 'Misc'

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def process_cc_statement(cc_df):
    # Starting Index
    start_idx = cc_df[cc_df['Unnamed: 2'].str.startswith('Transaction Date', na=False)].index[0]
    cc_df=cc_df.loc[start_idx:]

    # Selecting only desired columns
    desired_cols=['Unnamed: 2','Unnamed: 5','Unnamed: 10']
    cc_df=cc_df[desired_cols]

    # Making first row as Header
    cc_df.columns=cc_df.iloc[0]

    # Remove first row 
    cc_df.drop(cc_df.head(1).index,inplace=True) # drop first n rows

    # Adding New columns to match it with previous df
    # Adding Credit column
    cc_df['credit']=cc_df['Amount in INR']*0
    print(cc_df.columns)

    # Rename columns
    #print(cc_df.columns)
    name_dict={
    'Transaction Date:':'Date',
    'Transaction Details':'Transaction',
    'Amount in INR':'Debit',
    'credit':'Credit',
    }
    cc_df.rename(columns = name_dict, inplace = True)
    # Changing datatype
    # cc_df[["Debit", "Credit"]] = cc_df[["Debit", "Credit"]].apply(pd.to_numeric,errors='coerce')
    cc_df['Debit'] = cc_df['Debit'].str.replace(',', '').astype(float)
    cc_df['Credit']=pd.to_numeric(cc_df['Credit'])
    cc_df['Date'] = pd.to_datetime(cc_df['Date'], format='%d %b \'%y')
    cc_df['Date'] = cc_df['Date'].dt.strftime('%Y-%m-%d')
    cc_df['Tag']=[tag(i) for i in cc_df['Transaction']]



    cc_df['Month'] = [int(i.split('-')[1]) for i in cc_df['Date'] ]
    cc_df['Year'] = [int(i.split('-')[0]) for i in cc_df['Date'] ]
    print(cc_df.dtypes)
    return cc_df

# Scripting 
with st.sidebar:
    st.info("Upload your Credit Card statement or try this sample file [link](%s)" % url_credit)
    cc=st.file_uploader('',type=['xlsx,xls'],key='cc')

st.title('Axis Bank Credit Card Analyser')
if cc:
    try:
        cc_df = pd.read_excel(cc)
        cc_df=process_cc_statement(cc_df)
        st.write(cc_df)
    except:
        st.warning('Please enter the correct statement file')

st.markdown('---')
st.markdown('Made with :heart: by [Sahil Choudhary](https://www.sahilchoudhary.ml/)')
