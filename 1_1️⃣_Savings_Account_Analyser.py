# Spend Analyser

# Import Libraries
import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from datetime import datetime
import calendar
from babel.numbers import format_currency

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
            div.css-1r6slb0.e1tzin5v2{
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                padding: 5% 5% 5% 10%;
                border-radius: 5px;
                border-left: 0.5rem solid #9AD8E1 !important;
                box-shadow: 0 0.15rem 1.75rem 0 rgb(58 59 69 / 15%) !important;
            }
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
            return i.split('/')[3]
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

def process_savings_acc_statement(ss_df):

    # Starting Index
    start_idx = ss_df[ss_df['Name :- SAHIL CHOUDHARY'].str.startswith('SRL NO', na=False)].index[0]
    
    # Ending Index
    end_idx = ss_df[ss_df['Name :- SAHIL CHOUDHARY'].str.startswith('Unless', na=False)].index[0]
    ss_df = ss_df.iloc[start_idx:end_idx]

    # Selecting only desired columns
    desired_cols=['Unnamed: 1','Unnamed: 3','Unnamed: 4','Unnamed: 5']
    ss_df=ss_df[desired_cols]
 
    # Making first row as Header
    ss_df.columns=ss_df.iloc[0]

    # Remove first row 
    ss_df.drop(ss_df.head(1).index,inplace=True) # drop first n rows

    # Remove last row
    ss_df.drop(ss_df.tail(1).index,inplace=True) # drop last n rows

    # Rename columns
    #print(ss_df.columns)
    name_dict={ 
    'Tran Date':'Date',
    'PARTICULARS':'Transaction',
    'DR':'Debit',
    'CR':'Credit',
    }
    ss_df.rename(columns = name_dict, inplace = True)

    # Changing datatype
    ss_df[["Debit", "Credit"]] = ss_df[["Debit", "Credit"]].apply(pd.to_numeric,errors='coerce')
    

    ss_df['Date'] = pd.to_datetime(ss_df.Date, format='%d-%m-%Y')
    ss_df['Date'] = ss_df['Date'].dt.strftime('%Y-%m-%d')


    # Adding Tag column

    # Zomato
    ss_df['Tag']=[tag(i) for i in ss_df['Transaction']]
    
    ss_df['Month'] = [int(i.split('-')[1]) for i in ss_df['Date'] ]
    ss_df['Year'] = [int(i.split('-')[0]) for i in ss_df['Date'] ]
    return ss_df

# Scripting 
with st.sidebar:
    st.info("Upload your Savings Account statement or try this sample file [link](%s)" % url_saving)
    ss=st.file_uploader('',type=['xlsx'],key='savings')

st.title('Axis Bank Savings Account Analyser')

if ss:
    try:
        ss_df = pd.read_excel(ss)
        ss_df=process_savings_acc_statement(ss_df)

        # Get current month Analysis
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        ss1=ss_df[ss_df['Year']==currentYear]
        ss2=ss1[ss1['Month']==currentMonth]

        # Adding totals
        cm_debit=round(ss2['Debit'].sum(),1)
        cm_credit=round(ss2['Credit'].sum(),1)
        # Metrics
        col1,col2,col3=st.columns(3)
        col1.metric('This Month',calendar.month_name[currentMonth])
        col2.metric('Total Debit',cm_debit)
        col3.metric('Total Credit',cm_credit)


        # This Month Tables Row
        col1,col2=st.columns(2)
        with col1:
            st.info('Overview of Transactions')
            ss3 = ss2.groupby('Tag').sum('Debit')
            ss3=ss3.sort_values(by=['Debit'],ascending=False)
            st.write(ss3)
        with col2:
            st.info('Detailed Transaction History')
            ss2=ss2.sort_values(by=['Debit'],ascending=False)
            st.write(ss2)

    #-------------------------------Previous Month Analysis
    # Get Previous month Analysis
        currentYear = datetime.now().year
        prevMonth = (datetime.now().month)-1
        ss4=ss_df[ss_df['Year']==currentYear]
        ss5=ss4[ss4['Month']==prevMonth]
        # Adding totals
        pm_debit=round(ss5['Debit'].sum(),1)
        pm_credit=round(ss5['Credit'].sum(),1)
        # Metrics
        col1,col2,col3=st.columns(3)
        col1.metric('Previous Month',calendar.month_name[prevMonth])
        col2.metric('Total Debit',pm_debit)
        col3.metric('Total Credit',pm_credit)


    # Previous Month Tables Row
        col1,col2=st.columns(2)
        with col1:
            st.info('Overview of Transactions')
            ss6 = ss5.groupby('Tag').sum('Debit')
            ss6=ss6.sort_values(by=['Debit'],ascending=False)
            st.write(ss6)
        with col2:
            st.info('Detailed Transaction History')
            ss5=ss5.sort_values(by=['Debit'],ascending=False)
            st.write(ss5)  
    except:
        st.warning('Please enter the correct statement file')

st.markdown('---')
st.markdown('Made with :heart: by [Sahil Choudhary](https://www.sahilchoudhary.ml/)')

