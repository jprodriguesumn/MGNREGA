from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import time
import datetime
import os
import pandas as pd
from random import randint
import platform
import csv


from india_funs import get_jobcard_info
 

time_delay = 1



## url of the website to choose state
url = 'http://nrega.nic.in/netnrega/statepage.aspx?Page=C&Digest=GmpYzpnzFJIVhl6rY0MeSw'

#Distinguish when running this from laptop vs Fed desktop
if platform.system() == 'Windows':
    wd=webdriver.Chrome("C:/Users/irjpf02/Documents/Python Scripts/chromedriver.exe")
else: ##when working on my mac
    wd=webdriver.Chrome("/Users/joaorodrigues/Downloads/chromedriver")
##
wd.get(url)

stateN = '18'
yearN = '2' #2 to 11
districN = '09'
blockN = '001'
panchayatN = '001'
cardN = '2' ###start at 2

## choose state 18
#stateN = '18'
wd.get("http://nregasp2.nic.in/netnrega/loginframegp.aspx?page=C&state_code="+str(stateN))

#state = wd.find_element(By.XPATH,'//*[@id="form1"]/table[2]/tbody/tr[10]/td[2]/a')
#state.click()
time.sleep(time_delay)

## choose
#yearN = '2' #2 to 11
year = wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlFin"]/option['+yearN+']')
year.click()
time.sleep(time_delay)

## district
#districN = '09'
district = wd.find_element_by_xpath("//*[@value="+stateN+districN+"]")
district.click()
time.sleep(time_delay)

## block
#blockN = '001'
block = wd.find_element_by_xpath("//*[@value="+stateN+districN+blockN+"]")
block.click()
time.sleep(time_delay)

## Pan
#panchayatN = '001'
panchayat = wd.find_element_by_xpath("//*[@value="+stateN+districN+blockN+panchayatN+"]")
panchayat.click()
time.sleep(time_delay)

## Proceed
proceed = wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btProceed"]')                                
proceed.click()
time.sleep(time_delay)

## job card
#cardN = '2' ###start at 2
jobcard = wd.find_element_by_xpath("/html/body/form/center/table/tbody/tr["+cardN+"]/td[2]/a")
jobcard.click()

soup = BeautifulSoup(wd.page_source,"html5lib")




def uncover(stateN,districtN,blockN,panchayatN):
    url = 'http://nrega.nic.in/netnrega/statepage.aspx?Page=C&Digest=GmpYzpnzFJIVhl6rY0MeSw'

    #Distinguish when running this from laptop vs Fed desktop
    if platform.system() == 'Windows':
        wd=webdriver.Chrome("C:/Users/irjpf02/Documents/Python Scripts/chromedriver.exe")
    else: ##when working on my mac
        wd=webdriver.Chrome("/Users/joaorodrigues/Downloads/chromedriver")
    ##
    wd.get(url)

    ## choose state 18
    
    wd.get("http://nregasp2.nic.in/netnrega/loginframegp.aspx?page=C&state_code="+str(stateN))

    #state = wd.find_element(By.XPATH,'//*[@id="form1"]/table[2]/tbody/tr[10]/td[2]/a')
    #state.click()
    time.sleep(time_delay)

    ## choose
    
    year = wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlFin"]/option['+yearN+']')
    year.click()
    time.sleep(time_delay)

    ## district
    
    district = wd.find_element_by_xpath("//*[@value="+stateN+districN+"]")
    district.click()
    time.sleep(time_delay)

    ## block
    
    block = wd.find_element_by_xpath("//*[@value="+stateN+districN+blockN+"]")
    block.click()
    time.sleep(time_delay)

    ## Pan
    
    panchayat = wd.find_element_by_xpath("//*[@value="+stateN+districN+blockN+panchayatN+"]")
    panchayat.click()
    time.sleep(time_delay)

    ## Proceed
    proceed = wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btProceed"]')                                
    proceed.click()
    time.sleep(time_delay)

    ## job card
    
    jobcard = wd.find_element_by_xpath("/html/body/form/center/table/tbody/tr["+cardN+"]/td[2]/a")
    jobcard.click()

    soup = BeautifulSoup(wd.page_source,"html5lib")
    return soup



#JC = get_jobcard_info(soup)
#print("Job card ID: "+JC['job_card_id'])

#import csv
#my_dict = {'1': 'aaa', '2': 'bbb', '3': 'ccc'}
#with open('test.csv', 'w') as f:
#    for key in JC.keys():
#        f.write("%s,%s\n"%(key,JC[key]))

#print(JC.items())
#w = csv.writer(open("jobcards.csv","w"))
#for key, val in JC.items():
#   w.writerow([key, val])
#//*[@id="ctl00_ContentPlaceHolder1_ddlFin"]/option[11]
