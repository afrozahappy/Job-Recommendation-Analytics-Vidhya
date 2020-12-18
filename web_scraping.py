from bs4 import BeautifulSoup
import lxml
import requests
import nltk
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
import string
import re



def get_soundex(token):
    """Get the soundex code for the string"""
    token = token.upper()

    soundex = ""
    
    # first letter of input is always the first letter of soundex
    soundex += token[0]
    
    # create a dictionary which maps letters to respective soundex codes. Vowels and 'H', 'W' and 'Y' will be represented by '.'
    dictionary = {"BFPV": "1", "CGJKQSXZ":"2", "DT":"3", "L":"4", "MN":"5", "R":"6", "AEIOUHWY":"."}
    
    for char in token[1:]:
        for key in dictionary.keys():
            if char in key:
                code = dictionary[key] 
                if code != '.': 
                    if code != soundex[-1]: 
                        soundex += code 
                    
    
    # trim or pad to make soundex a 4-character code
    soundex = soundex[:4].ljust(4, "0")
        
    return soundex



html_text=requests.get('https://jobsnew.analyticsvidhya.com/jobs/all').text
soup=BeautifulSoup(html_text,'lxml')
pages=soup.find('div',class_='pagination-div d-table mx-auto')
total_pages=pages.find('span',class_='current text-muted').text.strip().split(' ')[-1][0:-1]
skillset=['Sql','Python','Data Analysis','NLP','Data Visualization','Machine Learning',
          'Statistical Modelling','Data Mining','Regression','Classification','numpy',
          'pandas','Java','Data Analyst','Natural Language Processing','Web Scraping','Tableau',
          'time series','Data Science','Clustering','Decision Trees','Business Analysis',
          'Business Intelligence','sklearn','Maths','Analytics','Excel','ML']
skills_req=''
location=''
salary=''
experience=''
openings=''
unmatch_percent=0
nltk.download('wordnet')
lemmer = nltk.stem.WordNetLemmatizer()
tokenizer = nltk.RegexpTokenizer(r"\w+")
pref_locations=['Mumbai','Pune','Noida','Delhi','Bangalore','Kolkata','Gurgaon','Ghaziabad','Hyderabad','Multiple','Gurugram']

for i in range(1,int(total_pages)+1):
    print(f'Page No: {i}')
    dict_obj=dict()
    job_count=0
    html_text_page=requests.get('https://jobsnew.analyticsvidhya.com/jobs/all?page='+str(i)).text
    soup_page=BeautifulSoup(html_text_page,'lxml')
    page_details=soup_page.find('div',class_='pagination-div d-table mx-auto')
    jobs_page=soup_page.find_all('div',class_='col-lg-9 col-md-12 col-sm-12')
    for job in jobs_page:
        count=0
        job_link=job.a['href'].split('/')[-2]
        loc_url='https://jobsnew.analyticsvidhya.com/jobs/'+job_link+'/'
        html_job_text=requests.get('https://jobsnew.analyticsvidhya.com/jobs/'+job_link+'/').text
        soup_job=BeautifulSoup(html_job_text,'lxml')
        jobs_details=soup_job.find_all('div',class_='col-lg-8 col-md-8 col-sm-12')
        details=jobs_details[0].find_all('span')
        for detail in details:
            if detail.i['class'][-1]=='fa-map-marker-alt':
                location=detail.text
            elif detail.i['class'][-1]=='fa-wallet':
                salary=detail.text
            elif detail.i['class'][-1]=='fa-briefcase':
                experience=detail.text.split(':')[-1]
            elif detail.i['class'][-1]=='fa-users':
                openings=detail.text.split(':')[-1]
    
        desc=soup_job.find_all('div',class_='card-body')
        for each_desc in desc:
            if each_desc.find('h4')!=None and each_desc.h4['class'][0]=='job-details':
                skills_req=each_desc.find('h4',class_='skills heading-4').find_next('p').text.strip()
        
        lem_skillset=[lemmer.lemmatize(token.lower()) for token in skillset]
        all_skills=skills_req.split(',')
        req_skillset=[lemmer.lemmatize(token.lower()) for token in all_skills]
        total_skills_req=len(req_skillset)
        found=False
        for j in req_skillset:
            found=False
            for skills in lem_skillset:
                if(not found):
                    all_skills=re.split(r'[/\|&]',j)
                    for sk in all_skills:
                        if (nltk.edit_distance(skills, sk.strip())/len(sk.strip())<=0.2):
                            count=count+1
                            found=True
                            break
                
        unmatch_percent=count/total_skills_req*100;
        job_count=job_count+1
        start_year=re.split(r'[- ]',experience.strip())[0].strip()
        locs=location.split(',')
        loc_found=False
        for l in locs:
            for p in pref_locations:
                 if (re.search(p.lower(), l.strip().lower())!=None or (get_soundex(p)==get_soundex(l.strip()))):
                    loc_found=True
        if loc_found and int(start_year)<=3 and unmatch_percent>0:
            dict_obj[job_count]={'Company': job.p.text,'Title':job.a.h6.text,'Location':location,'Salary':salary,'Experience':experience,
                             'Openings':openings,'Skills_match':unmatch_percent,'Url':loc_url}
       
        sorted_results=dict(sorted(dict_obj.items(), key = lambda x: (-x[1]['Skills_match'], i)))
        
    cnt=1
    for item in sorted_results.items():
        loc=item[1]['Location']
        sal=item[1]['Salary']
        exp=item[1]['Experience']
        op=item[1]['Openings']
        skl=item[1]['Skills_match']
        com=item[1]['Company']
        tit=item[1]['Title']
        url=item[1]['Url']
        
        print(cnt)
        print(f'Job Title: {tit}')
        print(f'Company Name: {com}')
        print(f'Job Location: {loc}')
        print(f'Salary offered: {sal}') 
        print(f'Experience required: {exp}')
        print(f'No of openings: {op}')
        print(f'Skills matched: {skl} %')
        print(f'To know more: {url}')
        print('')
        cnt+=1
    print('----------------------------------------------------XXXXXXXXXXXXXXX----------------------------------------------')
