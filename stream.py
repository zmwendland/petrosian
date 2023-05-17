# -*- coding: utf-8 -*-
"""
Created on Sun May 14 17:12:06 2023

@author: zwendland001
"""

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r 
import streamlit as st
from geopy.geocoders import Nominatim

st.set_page_config(
    page_title="Petrosian App - Beta",
    page_icon="",
)


def query():
        
    df = pd.read_csv('addys.csv')
    
    full_addy_list = list(df['address'])
    
    cnt = 0
    
    first_add = ''.join(str(full_addy_list[0]))
    first_add = first_add.replace(' ', '+')
    street_endings = ['St','Street','Ave','Avenue','Ln','Lane',
                      'Circle','Cir','Dr','Drive','Crossing','Xing',
                      'Blvd','Alley','Trail','Trl','Aly','Cove','CV',
                      'Boulevard','Causeway','CSWY','CTR','Center',
                      'Court','CT']
    
    url = 'https://www.georgiamls.com/real-estate/search-action.cfm?gtyp=addr&sid=0&styp=sale&address='+first_add+'&scat=1%2C2%2C3'
    
    page = r.get(url).text
    
    soup = bs(page,'html.parser')
    
    address =[]
    for x in soup.find_all('div',class_='col-xs-12 col-sm-6 col-md-3 text-center listing-gallery'):
        for y in x.find_all('p')[2]:
            z = y.text.strip()
            address.append(z)
    new_address = str(address[0].replace(' ','-'))+'-'
    
    
    bed_bath = []
    for x in soup.find_all('div',class_='col-xs-12 col-sm-6 col-md-3 text-center listing-gallery'):
        for y in x.find_all('p')[1]:
            z = y.text.strip()
            bed_bath.append(z)
    
    new_bb = str(bed_bath[0].replace('.',''))
    beds = new_bb.split()[0]
    baths = new_bb.split()[2]
    hbath = new_bb.split()[4]
    
    mls = []
    
    for x in soup.find_all('div',class_='col-xs-12 col-sm-6 col-md-3 text-center listing-gallery'):
        for y in x.find_all('p')[3]:
            z = y.text.strip()
            mls.append(z)
    
    real_mls = str(mls[0])
    real_mls = real_mls.split()[-1]
            
    city_state_zip = []        
    for x in soup.find_all('div',class_='col-xs-12 col-sm-6 col-md-3 text-center listing-gallery'):
            city_state_zip.append(x.find('br').content)
                
    addys = soup.find_all('p', limit=3)[-1]
    radd = ''.join(addys.find('br').next_siblings)
    city_state_zip = str(radd.strip())
    city_state_zip = city_state_zip.replace(',', '')
    city_state_zip = city_state_zip.replace(' ', '-')
    
    token = new_address+city_state_zip+'/'+real_mls
    
    new_url = 'https://www.georgiamls.com/'+token
    
    p2 = r.get(new_url).text
    
    soup2 = bs(p2,'html.parser')
    # table = soup2.find_all('td',class_='tr-label')
    
    dets = []
    for tr in soup2.select('tr:has(>td:contains("Bed/Bath"))~tr'):
        for td in tr.select("td"):
            z = td.text.strip()
            dets.append(z)
    
    
    labels = dets[::2]
    info = dets[1::2]
    subj_df = pd.DataFrame({'labels':labels,'data':info})
    # ldf.reset_index(inplace=True)
    schools = str(info[27])
    schools = schools.replace('\r\n\t\t\t\t\t\t\t\t', ' ')
    
    comps = []  
    for x in soup2.find_all('table',class_='table-condensed'):
        for y in x.find_all('a'):
            z = y.text.strip()
            comps.append(z)
    comps = [x.replace(' \r\n\t\t\t\t\t\t',',') for x in comps]
    comps = list(filter(None,comps))
    
    links = []
    for x in soup2.find_all('table',class_='table-condensed'):
        for y in x.find_all('a' ,href=True):
            z = y.get('href')
            links.append(z)
    links = ['https://www.georgiamls.com'+x for x in links]
    link_df = pd.DataFrame({'links':links})       
    link_df.drop_duplicates(inplace=True)
    new_df = pd.DataFrame()
    
    new_df['status'] = subj_df.iloc[0]
    new_df['rental_list'] = subj_df.iloc[1]
    new_df['property_type'] = subj_df.iloc[7]
    new_df['address'] = subj_df.iloc[4]
    new_df['sqft'] = subj_df.iloc[8]
    new_df['yoc']= subj_df.iloc[10]
    new_df['lot_size'] = subj_df.iloc[9]
    new_df['bsmt'] = subj_df.iloc[15]
    new_df['water'] = subj_df.iloc[26]
    new_df['taxes'] = subj_df.iloc[30][1]
    new_df['beds'] = beds
    new_df['baths'] = baths
    new_df['half_baths'] = hbath
    new_df['schools'] = schools
    
    new_df.reset_index(inplace=True)
    new_df.rename(columns={'index':'label'},inplace=True)
    new_df = new_df.iloc[1].T
    
    comp_df = pd.DataFrame()
    comp_df['Comp'] = comps
    comp_df['URL'] = list(link_df.links)
    return new_df, comp_df

# def near_comps():
    
new_df = query()[0]
comp_df = query()[1]
print(comp_df)
comp_df.to_csv('comps.csv')
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","Accept-Encoding":"gzip, deflate, br","upgrade-insecure-requests":"1"}

# st.file_uploader('Upload file')

inputForm = st.form("Address Input")
inputStreet = inputForm.text_input(label='Street',value='5945 Willow Oak Pass')
inputStreet = inputForm.text_input(label='City',value='Cumming')
inputStreet = inputForm.text_input(label='State',value='GA',max_chars=2)
inputStreet = inputForm.text_input(label='Zipcode',value='30040',max_chars=5)

submit_button = inputForm.form_submit_button("Find Value")

if submit_button:
    st.header('Subject Details')
    st.table(new_df)
    st.header('Comp Details')
    st.table(comp_df)


