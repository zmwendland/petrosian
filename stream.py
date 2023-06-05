# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:37:20 2023

@author: zwendland001
"""
import streamlit as st 
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep


st.set_page_config(
    page_title="Petrosian App - Beta",
    page_icon="",
)

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To readead()
    # st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file).dropna()
    
    st.table(df.Address)
    
    addy_df = pd.DataFrame(df.Address,columns=['Address'])

    addy_df.dropna(inplace=True)
    address = list(addy_df.Address)
    st.write(address)
            
    cnt = 0 

    dfl = []
    while cnt < len(address):
        try:
            driver = webdriver.Chrome(executable_path = r'./chromedriver')
            
            
            url = 'https://www.gamls.com/'
            
            
            username = 'PETROSIANSAM'
            password = 'Stanley32!'
            
            driver.get(url)
            
            driver.find_element("name", "username").send_keys(username)
            sleep(1)
            # Find the password input field and send the password to the input field.
            driver.find_element("name", "password").send_keys(password)
            sleep(1)
            
            driver.find_element("name", "sendLogin").click()
            
            WebDriverWait(driver=driver, timeout=10).until(lambda x: x.execute_script("return document.readyState === 'complete'"))
            error_message = "Incorrect username or password."
            errors = driver.find_elements(By.CLASS_NAME, "flash-error")
        
            # When errors are found, the login will fail. 
            if any(error_message in e.text for e in errors): 
                print("[!] Login failed")
            else:
                print("[+] Login successful")
        
            sleep(3)        
        
        
            
            for x in address:
                street_name = x
                
                n = 2 
                
                sname = street_name.split(' ')[n-1]
                
                city = street_name.split(',')[1]
                city = str(city.strip())    
                
                url1 = 'https://members.gamls.com/searchv2/?Srch=1&GETLNS=Go&showControls=true&PROPERTYTYPE=Residential&DAYSBACK=any&FP=any&OOM=false&HASPHOTO=1&PROPERTYSUBTYPE_OP=O&QC=true&MLSSTATUS=Sold&CITY='+city+'&PROPERTYSUBTYPE=5803&MINCLOSEDATE=2023%2D01%2D01&PROPERTYCONDITION=any&STREETNAME='+sname+'&MAXCLOSEDATE=2023%2D06%2D04&LOCALSRCH=1'
                
                driver.get(url1)
                sleep(3)
                driver.find_element('name','GetLNs').click()
                
                mls = driver.find_element(By.CLASS_NAME,'me-4').text
                
                list_url = 'https://members.gamls.com/listingv2/detail/propertyType/Residential/listingID/'+mls
                sleep(2)
                driver.get(list_url)
                
                table = driver.find_element(By.TAG_NAME,'tbody').text    
                
                ltab = list(table.split('\n')) 
                ltab.remove('Projected Close:')
                ltab.remove('Own Condition:')
                
                headers = ltab[0::2]
                deets = ltab[1::2]
                
                dedf = pd.DataFrame(deets)
                
                # sleep(2)
                dedf.index = headers 
                
                dfl.append(dedf)
                
                cnt = cnt+1
           
        except:
            pass
            cnt = cnt+1

    for x in dfl:
        st.tablex(x)
