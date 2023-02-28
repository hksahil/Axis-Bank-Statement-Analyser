# Combined

# Import Libraries
import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from datetime import datetime
import calendar
from babel.numbers import format_currency
import plotly.express as px

# Page Settings
st.set_page_config(page_title='Spend Analyser',page_icon=':smile:',layout="wide")

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
def tag_savings(i):
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
    ss_df['Tag']=[tag_savings(i) for i in ss_df['Transaction']]
    
    ss_df['Month'] = [int(i.split('-')[1]) for i in ss_df['Date'] ]
    ss_df['Year'] = [int(i.split('-')[0]) for i in ss_df['Date'] ]
    return ss_df

def tag_credit(i):
    if 'ZOMATO' in i:
        return 'ZOMATO'
    elif 'SWIGGY' in i:
        return 'SWIGGY'
    elif 'ATM-CASH' in i:
        return 'CASH WITHDRAWL'
    elif 'Jio' in i:
        return 'JIO RECHARGE'
    elif 'ASTAR' in i:
        return 'SALARY CREDITED'
    elif 'PARVEEN' in i or 'Parvee' in i or 'Parveen' in i:
        return 'SENT TO PARVEEN'
    elif 'Dish' in i:
        return 'DISHTV'
    elif 'CreditCard' in i:
        return 'CC PAYMENT'
    elif 'Dominos' in i:
        return 'DOMINOS'
    else :
        try:
            return i.split(',')[0].upper()
        except:
            return 'MISC'

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
    cc_df['Tag']=[tag_credit(i) for i in cc_df['Transaction']]



    cc_df['Month'] = [int(i.split('-')[1]) for i in cc_df['Date'] ]
    cc_df['Year'] = [int(i.split('-')[0]) for i in cc_df['Date'] ]
    

    # Remove one row which has IB payment word in it from cc statement
    # Because it just tells you the bill payment of cc
    cc_df=cc_df[cc_df['Transaction'].str.contains('IB PAYMENT')==False]
    return cc_df

url_saving='https://drive.google.com/uc?export=download&id=1IINDYx3LOWVe-Kjv-8ohFksvPHw_87h8'
url_credit='https://drive.google.com/uc?export=download&id=1XWcrAQzwxNYHpKRMoFAp91GBTEaWgxb7'
# Scripting 
with st.sidebar:
    st.info("Upload your Savings Account statement or try this sample file [link](%s)" % url_saving)
    ss=st.file_uploader('',type=['xlsx'],key='ss')
    st.info("Upload your Credit Card statement or try this sample file [link](%s)" % url_credit)
    cc=st.file_uploader('',type=['xlsx'],key='cc')


st.title('Axis Bank Account Analyser')
if ss and cc:
    try:
        ss_df = pd.read_excel(ss)
        ss_df=process_savings_acc_statement(ss_df)

        cc_df = pd.read_excel(cc)
        cc_df=process_cc_statement(cc_df)

        #---------------------------Currrent Month Analysis Starts ---------------------------
        # Row 1 starts
        ss1=ss_df[ss_df['Year']==datetime.now().year]
        ss2=ss1[ss1['Month']==datetime.now().month]

        cc1=cc_df[cc_df['Year']==datetime.now().year]
        cc2=cc1[cc1['Month']==datetime.now().month]
        
        # Adding totals
        # Debit Calculation
        # To calculate debit of current month in best way: Follow this policy
        ## 1. Get total of ss df while ignoring credit card payment
        a=ss2[ss2['Transaction'].str.contains('CreditCard')==False]['Debit'].sum()
        ## 2. Get total of cc df while ignoring credit card payment ('IB PAYMENT')
        b=cc2['Debit'].sum()
        ## Add 1 and 2
        c=a+b
        cm_debit=round(ss2['Debit'].sum(),1)
        cm_credit=round(ss2['Credit'].sum(),1)
        # Metrics
        col1,col2,col3=st.columns(3)
        col1.metric('Month',calendar.month_name[datetime.now().month])
        col2.metric('Total Debit',format_currency(c, 'INR', locale='en_IN'))
        col3.metric('Total Credit',format_currency(cm_credit, 'INR', locale='en_IN'))

        # Row 1 ends
        # Row 2 starts
        col1,col2=st.columns(2)
        with col1:
            st.info('Overview of Savings Account Spends')
            ss4 = (ss2[~ss2['Transaction'].str.contains('CreditCard')]
            .groupby('Tag')
            .sum('Debit')
            .sort_values(by='Debit', ascending=False)[['Debit', 'Credit']]
            )
            ss4=ss4.sum(axis=0).to_frame('Total').T.append(ss4)
            st.dataframe(ss4)


        with col2:
            st.info('Overview of Credit Card Spends')
            cc3 = (cc2.groupby('Tag')
            .sum('Debit')
            .sort_values(by=['Debit'],ascending=False)[['Debit','Credit']])
            cc3=cc3.sum(axis=0).to_frame('Total').T.append(cc3)
            st.dataframe(cc3)
        
        # Row 2 ends


        # Detailed Savings acc transactions + Credit card transactions
        # Adding source to each df
        cc2['Source']='Credit Card'
        ss2['Source']='Savings Account'
        combined_df = ss2.append(cc2, ignore_index=True).sort_values(by=['Debit'],ascending=False)
        #cc12=cc11.sort_values(by=['Debit'],ascending=False)
        st.info('Detailed Savings account + Credit card transactions')
        # bar chart
        combined_df = combined_df.sort_values('Debit', ascending=False)
        #combined_df=combined_df.sum(axis=0).to_frame('Total').T.append(combined_df)
        fig = px.bar(combined_df, x="Tag", y="Debit", color="Source", text_auto=True)
        fig.update_traces(textangle=0, textposition="outside", cliponaxis=False)
        #fig.update_layout(yaxis={'Debit':'total ascending'}) # add only this line
        
        st.plotly_chart(fig, use_container_width=True)

        st.write(combined_df)
        #fig.show()
    except:
        st.warning('Please enter the correct statement files')

    #---------------------------Currrent Month Analysis Ends ---------------------------
    st.markdown('---')

    #---------------------------Previous Month Analysis Starts ---------------------------
    # # Row 1 starts
    # prevMonth = (datetime.now().month)-1
    # currentYear = datetime.now().year
    # ss10=ss_df[ss_df['Year']==currentYear]
    # ss11=ss10[ss10['Month']==prevMonth]

    # cc10=cc_df[cc_df['Year']==currentYear]
    # cc11=cc10[cc10['Month']==prevMonth]
    
    # # Adding totals
    # d=ss11[ss11['Transaction'].str.contains('CreditCard')==False]['Debit'].sum()
    # e=cc11[cc11['Transaction'].str.contains('CreditCard')==False]['Debit'].sum()
    # f=d+e
    # pm_debit=round(ss11['Debit'].sum(),1)
    # pm_credit=round(ss11['Credit'].sum(),1)
    # # Metrics
    # col1,col2,col3=st.columns(3)
    # col1.metric('Month',calendar.month_name[prevMonth])
    # col2.metric('Total Debit',f)
    # col3.metric('Total Credit',pm_credit)

    # # Row 1 ends

    # # Row 2 starts
    # col1,col2=st.columns(2)
    # with col1:
    #     st.info('Overview of Savings Account Spends')
    #     ss12 = ss11.groupby('Tag').sum('Debit')
    #     ss13=ss12.sort_values(by=['Debit'],ascending=False)
    #     st.write(ss13)
    # with col2:
    #     st.info('Overview of Credit Card Spends')
    #     cc12=cc11.sort_values(by=['Debit'],ascending=False)
    #     st.write(cc12)
    # # Row 2 ends

    # # Detailed Savings acc transactions + Credit card transactions
    # # Adding source to each df
    # cc3['Source']='Credit Card'
    # ss11['Source']='Savings Account'
    # combined_df_prev = ss11.append(cc12, ignore_index=True)
    # st.info('Detailed Savings acc transactions + Credit card transactions')
    # st.write(combined_df_prev)
    #---------------------------Previous Month Analysis Ends ---------------------------
st.markdown('Made with :heart: by [Sahil Choudhary](https://www.sahilchoudhary.ml/)')
