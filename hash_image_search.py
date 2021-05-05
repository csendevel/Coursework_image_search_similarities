import random
import pandas as pd
import numpy as np
import requests
import os
import re
import copy
import cv2
import wget
import urllib
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import html

#new features
arts_features = ('Original Title', 'Date', 'Style', 'Period', 'Genre', 'Media', 'Location', 'Wikipedia article', 'References', 'Wikiart art url', 'Wikiart image url')

my_dataset = pd.read_csv('./dataset.csv') #dataset for new features

author_page_link = {} 

authors = {} #art text-lists of authors

image_hashes = {}

def normalize_word(word):
    new_word = unidecode(word.lower()).replace('\\','').replace('\'','')
    return new_word

def find_author_page(author):
    if(author in author_page_link):
        return author_page_link[author]

    #url for searching author page
    url = 'https://www.wikiart.org/en/Search/' + author

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path=r'./chromedriver.exe', options=options)
    driver.get(url)

    if 'Sorry, nothing found' in driver.page_source:
            driver.quit()
            author_page_link[author] = ''
            return ''

    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    author_info = soup.find('div', {'class' : 'artist-name'})


    if(author_info):
        author_link = author_info.find('a', {'class' : 'ng-binding'}).get('href')
    else:
        author_link = ''

    author_page_link[author] = author_link

    driver.quit()
    
    del soup
    return author_link


def image_difference(image_link1, image_link2, full_image_name_1, full_image_name_2):
    _hash1=""
    _hash2=""
    
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    'ACCEPT-ENCODING' : 'gzip, deflate, br',
    'ACCEPT-LANGUAGE' : 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'REFERER' : 'https://www.google.com/'
    }

    if(full_image_name_1 in image_hashes):
        _hash1 = image_hashes[full_image_name_1]
    else:
        img1 = requests.get(image_link1, headers = headers)
        out = open(".\img1.jpg", "wb")
        out.write(img1.content)
        out.close()    

        image1 = cv2.imread(".\img1.jpg")
        resized = cv2.resize(image1, (8,8), interpolation = cv2.INTER_AREA) 
        gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        avg=gray_image.mean()
        ret, threshold_image = cv2.threshold(gray_image, avg, 255, 0)     
        
        os.remove(".\img1.jpg")

        _hash1=""
        for x in range(8):
            for y in range(8):
                val=threshold_image[x,y]
                if val==255:
                    _hash1=_hash1+"1"
                else:
                    _hash1=_hash1+"0"
        image_hashes[full_image_name_1] = _hash1

    if(full_image_name_2 in image_hashes):
        _hash2 = image_hashes[full_image_name_2]
    else:
        img2 = requests.get(image_link2, headers = headers)
        out = open(".\img2.jpg", "wb")
        out.write(img2.content)
        out.close()

        image2 = cv2.imread(".\img2.jpg") 
        resized = cv2.resize(image2, (8,8), interpolation = cv2.INTER_AREA) 
        gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        avg=gray_image.mean()
        ret, threshold_image = cv2.threshold(gray_image, avg, 255, 0)     
        
        os.remove(".\img2.jpg")

        _hash2=""
        for x in range(8):
            for y in range(8):
                val=threshold_image[x,y]
                if val==255:
                    _hash2=_hash2+"1"
                else:
                    _hash2=_hash2+"0"
        image_hashes[full_image_name_2] = _hash2
    
    l=len(_hash1)
    i = 0
    count = 0
    while i < l:
        if _hash1[i] != _hash2[i]:
            count = count + 1
        i = i + 1

    return count

def find_art(art_author, art_name, art_link):
    art_author_link = find_author_page(art_author)

    if(art_author_link == ''):
        return ''

    #author all works link
    search_url = 'https://www.wikiart.org' + art_author_link + '/all-works/text-list'
    
    
    if(not art_author in authors):
        r = requests.get(search_url)
        soup = BeautifulSoup(r.text, 'lxml')

        art_works = soup.find('ul', {'class':'painting-list-text'})
        if(art_works != None):
            art_works = art_works.find_all('li', {'class':'painting-list-text-row'})
        else:
            return ''

        authors[art_author] = copy.copy(art_works)
        
    else:
        art_works = authors[art_author]

    ref = ''
    
    for names in art_works:
        art_work_ref = 'https://www.wikiart.org' + names.find('a').get('href')
        
        page = requests.get(art_work_ref)
        soup = BeautifulSoup(page.text, 'lxml')
        
        tmp_art_name = re.sub('<span>.*</span>|\n', '', names.__repr__())
        second_art_name = re.sub('\n|<.*?>|\s{2,}?|,|\'', '', tmp_art_name.__repr__())

        image_url = soup.find('meta', {'property':'og:image'})
        valid_image_url = (image_url.__repr__()).split('"')[1]

        diff = image_difference(art_link, valid_image_url, art_author+art_name, art_author+second_art_name)

        if diff < 8:
            ref = art_work_ref
            break

    return ref

n = len(my_dataset) #arts number

for i in range(n):
    art_author = normalize_word(my_dataset.iloc[i, 2])
    art_name = normalize_word(my_dataset.iloc[i, 3])
    art_link = my_dataset.iloc[i, 23]

    url = ''
    if(art_link != '' or art_link != '—'):
        url = find_art(art_author, art_name, art_link)

    if url == '':
        print(i, "success")
        continue

    text = requests.get(url).text
    soup = BeautifulSoup(text, "lxml")

    my_dataset['Wikiart art url'][i] = url

    #extract features
    references = soup.find('div', {'class': 'info-tab-links-external'})
    if references != None:
        references = re.sub('\n|<.*?>|\s{1,}?', '', references.__repr__())
        my_dataset['References'][i] = references


    wiki_des = soup.find('div', {'id':'info-tab-wikipediadescription'})
    if wiki_des != None:
        wiki_des = re.sub('\n|<.*?>|\s{2,}?', '',  wiki_des.__repr__())
        my_dataset['Wikipedia article'][i] = wiki_des

    #find image url for algo v.2
    image_url = soup.find('meta', {'property':'og:image'})
    valid_image_url = (image_url.__repr__()).split('"')[1]

    my_dataset['Wikiart image url'][i] = valid_image_url

    art_info = soup.find('article').find('ul').find_all('li')

    if art_info != []:
        features = []

        for item in art_info:
            features.append(re.sub('\n|<.*?>|\s{2,}?', '', item.__repr__()))

        for strings in features:
            tmp = strings.split(':')
            if tmp[0] in arts_features:
                my_dataset[tmp[0]][i] = tmp[1]

    print(i, "success")

#data export
my_dataset.to_excel('./new_dataset_2.xlsx')

my_dataset.to_csv('./dataset.csv', index =False)
