"""
Joao Rodrigues, Sep 1st 2018
Federal Reserve Bank of Minneapolis, Minneapolis MN

These codes access India ob guarantee progam website,
downloads the job card of a person, and downloads the information into
a dataset. 
"""


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


def open_state(stateN,wd):
    """
    #####Inputs#####
    stateN: string with state code
    wd: webdriver object (chromedriver here)
    
    #####Outputs#####
    action: It just opens the stateN form page
    """
    wd.get("http://nrega.nic.in/netnrega/statepage.aspx?Page=C&Digest=GmpYzpnzFJIVhl6rY0MeSw")

    wd.find_element_by_css_selector("a[href*='code="+stateN+"']").click()

    try:
        assert 'loginframe' in wd.title 
    except AssertionError:
        print("state page did not load")
    
    return


def GetCodes(stateN,wd):
    """
    #####Inputs#####
    stateN: string with state code
    wd: webdriver object (chromedriver here)
    
    #####Outputs#####
    obs: list with (panchayat code,year) pairs (dictionaries)
    """
    #open state
    open_state(stateN,wd)

    obs = []
    OldOptions = []
    WaitTime = 5
    Years = Select(wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlFin"]'))
    YearsNum = len(Years.options)
    for year in range(1,YearsNum):
        #Select year
        Years.select_by_index(year)

        #Wait until districts are loaded
        WebDriverWait(wd,WaitTime).until(
            EC.text_to_be_present_in_element_value((
                By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]/option[2]'),stateN))

        #Get district code texts and count of districts in this year
        soup = BeautifulSoup(wd.page_source,"xml")
        Districts = soup.find('select',id="ctl00_ContentPlaceHolder1_ddlDistrict").find_all('option') #stores distrit codes
        DistrictsNum = len(Districts)

        #loop through districts
        for district in Districts[1:DistrictsNum]: #exclude first obs which is the select button
            #Select district
            print(district['value'])
            DistrictClick = WebDriverWait(wd,WaitTime).until(
                EC.presence_of_element_located((By.XPATH,'//*[@value='+district['value']+']')))
            DistrictClick.click()

            #Make sure blocks update
            try:
                WebDriverWait(wd,WaitTime).until(
                    EC.text_to_be_present_in_element_value((
                        By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_ddlBlock"]/option[2]'),district['value']))
            except TimeoutException :
                WebDriverWait(wd,WaitTime).until(
                    EC.presence_of_element_located((
                        By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_ddlBlock"]/option[1]')))
                

            #Get block code texts 
            soup = BeautifulSoup(wd.page_source,"xml")
            Blocks = soup.find('select',id="ctl00_ContentPlaceHolder1_ddlBlock").find_all('option') #stores block codes
            BlocksNum = len(Blocks)

            #loop through blocks
            for block in Blocks[1:BlocksNum]:
                #In no blocks uncovered
                if BlocksNum == 1:
                    print('No blocks in this district')
                    continue

                print(block['value'])

                #Select district            
                BlockClick = WebDriverWait(wd,WaitTime).until(
                    EC.presence_of_element_located((By.XPATH,'//*[@value='+block['value']+']')))
                BlockClick.click()

                #Make sure Panchayats update
                try:
                    WebDriverWait(wd,WaitTime).until(
                    EC.text_to_be_present_in_element_value((
                        By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_ddlPanchayat"]/option[2]'),block['value'] or '1822004'))
                except TimeoutException:
                    WebDriverWait(wd,WaitTime).until(
                        EC.presence_of_element_located((
                            By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_ddlPanchayat"]/option[1]')))

                #Get Panchayat code texts 
                soupB = BeautifulSoup(wd.page_source,"xml")
                PanOptions = soupB.find('select',id="ctl00_ContentPlaceHolder1_ddlPanchayat").find_all('option') #stores panchayat codes
                PanchayatsNum = len(PanOptions)

                #Check that there are any Panchayats
                if PanchayatsNum==1:
                    print('No Panchaysts in this block')
                    continue

                if (PanOptions == OldOptions) and (Oldyear==year):
                    print('Panchayats did not update')

                for option in PanOptions[1:PanchayatsNum]:
                    YearPan = {}
                    print(option['value'])
                    YearPan['year'] = year
                    YearPan['panchayat'] = option['value'] 
                    obs.append(YearPan)

                #Create old options
                OldOptions = PanOptions
                Oldyear = year

    return obs


def get_jobcard_info(soupy):

    #Fill a dictionary
    job_card_info = {}

    #Get tables from the form
    job_card_tables = soupy.find_all('table')

    def GetID(name,applicants):
        for app in applicants:
            if name == app['name']:
                return app['ID']
                break

        return 'No IDs found'

    ###########################################################
    #
    #Get job card information
    #
    #####################################################
    #family info table
    family_info_table = job_card_tables[1] #second table in the list of tables

    #Get all rows of family table
    family_info_rows = family_info_table.find_all('tr')

    #get job card number and family id
    job_card_info['job_card_id'] = family_info_rows[2].find_all('td')[1].b.text.strip()
    job_card_info['family_id'] = family_info_rows[2].find_all('td')[3].b.text.strip()
    job_card_info['hhd_head'] = family_info_rows[3].find_all('td')[1].b.text.strip()
    job_card_info['hhd_father_husband'] = family_info_rows[5].find_all('td')[1].text.strip()
    job_card_info['category'] = family_info_rows[6].find_all('td')[1].text.strip()
    job_card_info['date_of_registration'] = family_info_rows[7].find_all('td')[1].text.strip()
    job_card_info['address'] = family_info_rows[8].find_all('td')[1].text.strip()
    job_card_info['villages'] = family_info_rows[9].find_all('td')[1].text.strip()
    job_card_info['panchayat'] = family_info_rows[10].find_all('td')[1].text.strip()
    job_card_info['block'] = family_info_rows[11].find_all('td')[1].text.strip()
    job_card_info['district'] = family_info_rows[12].find_all('td')[1].text.strip()
    job_card_info['BPL_family?'] = family_info_rows[13].find_all('td')[1].text.strip()
    job_card_info['BPL_number'] = family_info_rows[13].find_all('td')[3].text.strip()
    job_card_info['epic_number'] = family_info_rows[14].find_all('td')[1].text.strip()


    ###############################################
    #
    #Family members on this job card
    #
    ################################################
    aplicants_info_table_rows = soupy.find('table',id="GridView4").find_all('tr',style="")
    AppN = len(aplicants_info_table_rows)
    hhdApplicants = []
    

    for applicant_row in range(1,AppN):
        try: ### if there is info to extract, do it
            table_cols = aplicants_info_table_rows[applicant_row].find_all('td')
            hhdApplicant = {}
            job_card_info['app_'+str(applicant_row)+'_num'] = table_cols[0].text.strip()
            job_card_info['app_'+str(applicant_row)+'_name'] = table_cols[1].text.strip()
            job_card_info['app_'+str(applicant_row)+'_gender'] = table_cols[2].text.strip()
            job_card_info['app_'+str(applicant_row)+'_age'] = table_cols[3].text.strip()
            job_card_info['app_'+str(applicant_row)+'_bank/postoffice'] = table_cols[4].text.strip()
            hhdApplicant['name'] = job_card_info['app_'+str(applicant_row)+'_name']
            hhdApplicant['ID'] = job_card_info['app_'+str(applicant_row)+'_num']
            hhdApplicants.append(hhdApplicant)
        except IndexError: ### otherwise it's just an empty cell
            job_card_info['app_'+str(applicant_row)+'_num'] = ''
            job_card_info['app_'+str(applicant_row)+'_name'] = ''
            job_card_info['app_'+str(applicant_row)+'_gender'] = ''
            job_card_info['app_'+str(applicant_row)+'_age'] = ''
            job_card_info['app_'+str(applicant_row)+'_bank/postoffice'] = ''



    ###############################################
    #
    #Requested Period of Employment
    #
    ################################################
    HasInfo = soupy.find('table',id="GridView1")
    if HasInfo:
        RequestsRows = soupy.find('table',id="GridView1").find_all('tr',style="")
        RequestN = len(RequestsRows)

        for request in range(1,RequestN):
            try:
                table_cols = RequestsRows[request].find_all('td')
                job_card_info['req_'+str(request)+'_num'] = table_cols[0].text.strip()
                job_card_info['req_'+str(request)+'_demand_id'] = table_cols[1].text.strip()
                job_card_info['req_'+str(request)+'_name_of_applicant'] = table_cols[2].text.strip()
                job_card_info['req_'+str(request)+'_applicantID'] = GetID(job_card_info['req_'+str(request)+'_name_of_applicant'],hhdApplicants)
                job_card_info['req_'+str(request)+'_date_employment_requested'] = table_cols[3].text.strip()
                job_card_info['req_'+str(request)+'_num_of_days'] = table_cols[4].text.strip()                
            except IndexError:
                job_card_info['req_'+str(request)+'_num'] = ''
                job_card_info['req_'+str(request)+'_demand_id'] = ''
                job_card_info['req_'+str(request)+'_name_of_applicant'] = ''
                job_card_info['req_'+str(request)+'_applicantID'] = ''
                job_card_info['req_'+str(request)+'_date_employment_requested'] = '' 
                job_card_info['req_'+str(request)+'_num_of_days'] = ''

    ###############################################
    #
    #Period and Work on which Employment Offered
    #
    ################################################
    MaxOffers = 151
    HasInfo = soupy.find('table',id="GridView2")
    if HasInfo:
        OffersRows = soupy.find('table',id="GridView2").find_all('tr',style="")
        OffersN = len(OffersRows)

        for offer in range(1,OffersN):
            try:
                table_cols = OffersRows[offer].find_all('td')
                job_card_info['offer_'+str(offer)+'_num'] = table_cols[0].text.strip()
                job_card_info['offer_'+str(offer)+'_demand_id'] = table_cols[1].text.strip()
                job_card_info['offer_'+str(offer)+'_name_of_applicant'] = table_cols[2].text.strip()
                job_card_info['offer_'+str(offer)+'_applicantID'] = GetID(job_card_info['offer_'+str(offer)+'_name_of_applicant'],hhdApplicants)
                job_card_info['offer_'+str(offer)+'_date_employment_requested'] = table_cols[3].text.strip()
                job_card_info['offer_'+str(offer)+'_num_of_days'] = table_cols[4].text.strip()
                job_card_info['offer_'+str(offer)+'_work_name'] = table_cols[5].text.strip()
            except IndexError:
                job_card_info['offer_'+str(offer)+'_num'] = ''
                job_card_info['offer_'+str(offer)+'_demand_id'] = ''
                job_card_info['offer_'+str(offer)+'_name_of_applicant'] = ''
                job_card_info['offer_'+str(offer)+'_applicantID'] = ''
                job_card_info['offer_'+str(offer)+'_date_employment_requested'] = ''
                job_card_info['offer_'+str(offer)+'_num_of_days'] = ''
                job_card_info['offer_'+str(offer)+'_work_name'] = ''


    ###############################################
    #
    #Period and Work on which Employment Given
    #
    ################################################
    HasInfo = soupy.find('table',id="GridView3")
    if HasInfo:
        CompletesRows = soupy.find('table',id="GridView3").find_all('tr',style="")
        CompletesN = len(CompletesRows)

        for complete in range(1,CompletesN):
            try:
                table_cols = CompletesRows[complete].find_all('td')
                if table_cols[1].find('b') != None: 
                    #as we don't want to include the subtotal row in the data
                    continue                
                job_card_info['complete_'+str(complete)+'_num'] = table_cols[0].text.strip()
                job_card_info['complete_'+str(complete)+'_name_of_applicant'] = table_cols[1].text.strip()
                job_card_info['complete_'+str(complete)+'_applicantID'] = GetID(job_card_info['complete_'+str(complete)+'_name_of_applicant'],hhdApplicants)
                job_card_info['complete_'+str(complete)+'_date_from_which_employment_requested'] = table_cols[5].text.strip()            
                job_card_info['complete_'+str(complete)+'_num_of_days'] = table_cols[3].text.strip()
                job_card_info['complete_'+str(complete)+'_work_name'] = table_cols[4].text.strip()
                job_card_info['complete_'+str(complete)+'_MSR_num'] = table_cols[5].text.strip()
                job_card_info['complete_'+str(complete)+'_total_work_done'] = table_cols[6].text.strip()
                job_card_info['complete_'+str(complete)+'_payment_due'] = table_cols[7].text.strip()
            except IndexError:
                job_card_info['complete_'+str(complete)+'_num'] = ''
                job_card_info['complete_'+str(complete)+'_name_of_applicant'] = ''
                job_card_info['complete_'+str(complete)+'_name_of_applicant'] = ''
                job_card_info['complete_'+str(complete)+'_date_from_which_employment_requested'] = ''            
                job_card_info['complete_'+str(complete)+'_num_of_days'] = ''
                job_card_info['complete_'+str(complete)+'_work_name'] = ''
                job_card_info['complete_'+str(complete)+'_MSR_num'] = ''
                job_card_info['complete_'+str(complete)+'_total_work_done'] = ''
                job_card_info['complete_'+str(complete)+'_payment_due'] = ''
            


    return job_card_info



def scrape_data(panchas,stateN,wd):
    """
    #######Inputs####### 
    panchas: list of dictionaries with (panchayat code, year) pairs
    stateN: string with state code from 01 to XX
    wd: webdriver object 

    #######Outputs####### 
    cards: list with downloaded
    BadCards: list with cards not downloaded
    BadPanchayats: list with (panchayst code, year) pairs that did not load     
    """


    #Create array to put cards in
    cards = []
    BadPanchayats = []
    BadCards = []
    WaitTime = 5

    #loop through panchayats
    for pan in panchas: 
        yearN = pan['year'] #numeric character
        panchayatN = pan['panchayat']
        stateN = pan['panchayat'][0:2]
        districtN = pan['panchayat'][0:4]
        blockN = pan['panchayat'][0:7]

        #Open the state page to fill form
        open_state(stateN,wd)

        #Select year
        Years = Select(wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlFin"]'))
        Years.select_by_index(yearN)

        #Select district
        DistrictClick = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_element_located((By.XPATH,'//*[@value='+districtN+']')))
        DistrictClick.click()

        #Select block
        BlockClick = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_element_located((By.XPATH,'//*[@value='+blockN+']')))
        BlockClick.click()

        #Select panchayat
        PanchayatClick = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_element_located((By.XPATH,'//*[@value='+panchayatN+']')))
        PanchayatClick.click()

        #Proceed
        proceed = wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btProceed"]')                                
        proceed.click()
        print('Panchayat: '+panchayatN)

        if 'File is under process' in wd.page_source:
            BadPanchayat = {}
            BadPanchayat['year'] = yearN
            BadPanchayat['panchayat'] = panchayatN
            BadPanchayats.append(BadPanchayat)
            print("file under process")
            continue

        
        #ensure cards are discoverable
        CardPresent = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_all_elements_located((By.XPATH,'/html/body/form/center/table/tbody/tr[1]/td[1]')))

        soup = BeautifulSoup(wd.page_source,"html.parser")
        CardsN = len(soup.find('table',align="center").find_all('tr'))

        #skip panchayat if there are no cards
        if CardsN == 1:
            print("No cards in this Panchayat")
            continue

        #loop through cards
        for card in range(2,CardsN): 
            print('Card number: '+str(card))
            ####might not need this
            try:
                jobcard = wd.find_element_by_xpath("/html/body/form/center/table/tbody/tr["+str(card)+"]/td[2]/a")
                jobcard.click()
            except NoSuchElementException:
                print("No cards in this Panchayat")
                continue

            try:
                assert 'Job Card' in wd.title
            except AssertionError:
                ProblemeCard = {}
                ProblemeCard['panchayat'] = panchayatN
                ProblemeCard['year'] = yearN
                ProblemeCard['card number'] = card
                BadCards.append(ProblemeCard)
                wd.execute_script("window.history.go(-1)")
                print("no 'job card' in title")
                continue
            

            soup = BeautifulSoup(wd.page_source,"html.parser")
            JC = get_jobcard_info(soup)

            cards.append(JC)
            wd.execute_script("window.history.go(-1)")

    wd.close()
        
    return cards,BadCards,BadPanchayats


def DownloadPdfs(panchas,stateN,wd):
    """
    #######Inputs####### 
    panchas: list of dictionaries with (panchayat code, year) pairs
    stateN: string with state code from 01 to XX
    wd: webdriver object 

    #######Outputs####### 
    cards: list with downloaded
    BadCards: list with cards not downloaded
    """

    
    open_state(stateN,wd)
    
    #Create arrays to put cards in
    cards = []
    BadPanchayats = []
    BadCards = []
    WaitTime = 5

    #loop through panchayats
    for pan in panchas: 
        yearN = pan['year'] #numeric character
        panchayatN = pan['panchayat']
        stateN = pan['panchayat'][0:2]
        districtN = pan['panchayat'][0:4]
        blockN = pan['panchayat'][0:7]

        #Select year
        Years = Select(wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlFin"]'))
        Years.select_by_index(yearN)

        #Select district
        DistrictClick = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_element_located((By.XPATH,'//*[@value='+districtN+']')))
        DistrictClick.click()

        #Select block
        BlockClick = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_element_located((By.XPATH,'//*[@value='+blockN+']')))
        BlockClick.click()

        #Select panchayat
        PanchayatClick = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_element_located((By.XPATH,'//*[@value='+panchayatN+']')))
        PanchayatClick.click()

        #Proceed
        proceed = wd.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btProceed"]')                                
        proceed.click()
        print('Panchayat: '+panchayatN)

        if 'File is under process' in wd.page_source:
            BadPanchayat = {}
            BadPanchayat['year'] = yearN
            BadPanchayat['panchayat'] = panchayatN
            BadPanchayats.append(BadPanchayat)
            continue

        
        #ensure cards are discoverable
        CardPresent = WebDriverWait(wd,WaitTime).until(
            EC.presence_of_all_elements_located((By.XPATH,'/html/body/form/center/table/tbody/tr[1]/td[1]')))

        soup = BeautifulSoup(wd.page_source,"html.parser")
        CardsN = len(soup.find('table',align="center").find_all('tr'))

        #If there are no cards CardsN == 1
        if CardsN == 1:
            print("No cards in this Panchayat")
            continue

        #loop through cards
        for card in range(2,CardsN):    #looping throuh rows of table
            print('Card number: '+str(card))
            #try:
            #    jobcard = wd.find_element_by_xpath("/html/body/form/center/table/tbody/tr["+str(card)+"]/td[2]/a")
            #    jobcard.click()
            #except NoSuchElementException:
            #    print("No cards in this Panchayat")
            #    continue

            try:
                assert 'Job Card' in wd.title
            except AssertionError:
                ProblemeCard = {}
                ProblemeCard['panchayat'] = panchayatN
                ProblemeCard['year'] = yearN
                ProblemeCard['card number'] = card
                BadCards.append(ProblemeCard)
            
            #save as pdf
            try : 
                pdfkit.from_string(wd.page_source, 'job_cards/'+ str(yearN) + '_' + JC['job_card_id'].replace('/','-') + '.pdf')
            except OSError:
                pass

            #go back to jobcard list
            wd.execute_script("window.history.go(-1)")

        #After all the cards are uploaded, return to form to fill
        open_state(stateN,wd)

    #close chromedriver
    wd.close()
        
    return cards,BadCards,BadPanchayats




def FixCards(DictionaryList):
    """
    Takes a list whose element is a dictionary with the variables found in each card
    then adjusts each element so that each dictionary at the end has the same keys 
    and can be easily turned into a dataset using json

    Input: Dictionary list with job cards and different keys
    Output: Dictionary list with job cards and same keys
    """

    #counting apps, reqs, offers, and completes to add accordingly
    def CountApps(card):
        NumOcc = sum(item.count('app_') for item in list(card.keys()))//5
        return NumOcc

    def CountReqs(card):
        NumOcc = sum(item.count('req_') for item in list(card.keys()))//5
        return NumOcc

    def CountOffers(card):
        NumOcc = sum(item.count('offer_') for item in list(card.keys()))//6
        return NumOcc

    def CountCompletes(card):
        NumOcc = sum(item.count('complete_') for item in list(card.keys()))//8
        return NumOcc

    AppMax = max([CountApps(card) for card in DictionaryList])
    ReqMax = max([CountReqs(card) for card in DictionaryList])
    OfferMax = max([CountOffers(card) for card in DictionaryList])
    CompleteMax = max([CountCompletes(card) for card in DictionaryList])

    for JobCard in DictionaryList:
        #Fix family applicants
        AppNumCurrent = CountApps(JobCard)
        for app in range(AppNumCurrent+1,AppMax+1):
            JobCard['app_'+str(app)+'_num'] = ''
            JobCard['app_'+str(app)+'_name'] = ''
            JobCard['app_'+str(app)+'_gender'] = ''
            JobCard['app_'+str(app)+'_age'] = ''
            JobCard['app_'+str(app)+'_bank/postoffice'] = ''

        #Fix requests
        ReqNumCurrent = CountReqs(JobCard)
        for request in range(ReqNumCurrent+1,ReqMax+1):
            JobCard['req_'+str(request)+'_num'] = ''
            JobCard['req_'+str(request)+'_demand_id'] = ''
            JobCard['req_'+str(request)+'_name_of_applicant'] = '' 
            JobCard['req_'+str(request)+'_date_employment_requested'] = '' 
            JobCard['req_'+str(request)+'_num_of_days'] = ''

        #Fix offers
        OfferNumCurrent = CountOffers(JobCard)
        for offer in range(OfferNumCurrent+1,OfferMax+1):
            JobCard['offer_'+str(offer)+'_num'] = ''
            JobCard['offer_'+str(offer)+'_demand_id'] = ''
            JobCard['offer_'+str(offer)+'_name_of_applicant'] = ''
            JobCard['offer_'+str(offer)+'_date_employment_requested'] = ''
            JobCard['offer_'+str(offer)+'_num_of_days'] = ''
            JobCard['offer_'+str(offer)+'_work_name'] = ''

        #Fix completes
        CompleteNumCurrent = CountCompletes(JobCard)
        for complete in range(CompleteNumCurrent+1,CompleteMax+1):
            JobCard['complete_'+str(complete)+'_num'] = ''
            JobCard['complete_'+str(complete)+'_name_of_applicant'] = ''
            JobCard['complete_'+str(complete)+'_date_from_which_employment_requested'] = ''            
            JobCard['complete_'+str(complete)+'_num_of_days'] = ''
            JobCard['complete_'+str(complete)+'_work_name'] = ''
            JobCard['complete_'+str(complete)+'_MSR_num'] = ''
            JobCard['complete_'+str(complete)+'_total_work_done'] = ''
            JobCard['complete_'+str(complete)+'_payment_due'] = ''

    return DictionaryList, AppMax,ReqMax,OfferMax,CompleteMax

            

###################################
# Generate CSV file
###################################
def SaveFile(cards,filename):
    """
    cards: list of dictionaries with balanced (same) keys
    """
    csv_columns = list(cards[0].keys())
    datafile = cards
    csv_file = filename+".csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in datafile:
                writer.writerow(data)
    except IOError:
        print("I/O error")

    return cards
