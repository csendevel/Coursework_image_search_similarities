import random
import pandas as pd
import numpy as np
import requests
import re
import copy
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import html

#new features
arts_features = ('Original Title', 'Date', 'Style', 'Period', 'Genre', 'Media', 'Location', 'Wikipedia article', 'References')

my_dataset = pd.read_csv('./dataset.csv') #dataset for new features

author_page_link = {} 

authors = {} #art text-lists of authors

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
    driver = webdriver.Firefox(options=options)
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


def find_art(art_author, art_name):
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
        tmp_art_name = re.sub('<span>.*</span>|\n', '', names.__repr__())
        
        new_art_name = re.sub('\n|<.*?>|\s{2,}?|,|\'', '', tmp_art_name.__repr__())
 
        new_art_name = new_art_name.lower().replace(' ','')
        art_name = art_name.lower().replace(' ','')
        
        if new_art_name == art_name:
            art_work_ref = names.find('a').get('href')
            ref = 'https://www.wikiart.org' + art_work_ref
            break

    return ref

my_dataset['References'] = ''
my_dataset['Wikipedia article'] = ''
my_dataset['Date'] = ''
my_dataset['Location'] = ''
my_dataset['Original Title'] = ''
my_dataset['Style'] = ''
my_dataset['Period'] = ''
my_dataset['Genre'] = ''
my_dataset['Media'] = ''

n = len(my_dataset) #arts number

for i in range(n):
    art_author = normalize_word(my_dataset.iloc[i, 2])
    art_name = normalize_word(my_dataset.iloc[i, 3])
    
    print(art_author, art_name)

    url = find_art(art_author, art_name)

    
    if url == '':
        print(i, "success")
        continue

    text = requests.get(url).text
    soup = BeautifulSoup(text, "lxml")

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
my_dataset.to_excel('./new_dataset.xlsx')
my_dataset.to_csv('./dataset.csv', index =False)

#print(my_dataset)
