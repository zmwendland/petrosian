# -*- coding: utf-8 -*-
"""
Created on Tue May 23 16:52:28 2023

@author: zwendland001
"""

import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup as bs
import requests as r 

st.set_page_config(
    page_title="Bulk Upload",
    page_icon="",
)

uploaded_file = st.file_uploader('Upload Files')


if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    # st.read(raw)
    st.header('Subjects:')
    st.write(df)
    cnt = 0
    
    full_addy_list = list(df['Address'])
    len_df = len(df)
    
    while cnt < len_df:
        
        zippers = []
        zip_code = full_addy_list[-5:]
        zippers.append(zip_code)
        
        st.write(pd.DataFrame(zippers))
        
        
        first_add = ''.join(str(full_addy_list[0]))
        first_add = first_add.replace(' ', '+')
        street_endings = ['St','Street','Ave','Avenue','Ln','Lane',
                          'Circle','Cir','Dr','Drive','Crossing','Xing',
                          'Blvd','Alley','Trail','Trl','Aly','Cove','CV',
                          'Boulevard','Causeway','CSWY','CTR','Center',
                          'Court','CT']
        
        url = 'https://www.georgiamls.com/real-estate/search-action.cfm?gtyp=addr&sid=0&styp=sale&address='+first_add+'&scat=1%2C2%2C3'
        
        page = r.get(url,headers=headers).text
        
        soup = bs(page,'html.parser')
        
        address =[]
        for x in soup.find_all('div',class_='col-xs-12 col-sm-6 col-md-3 text-center listing-gallery'):
            for y in x.find_all('p')[2]:
                z = y.text.strip()
                address.append(z)
        new_address = str(address[0]).replace(' ','-')+'-'
        
        
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
        cnt +=1
    
st.table(new_df)
st.table(comp_df)
