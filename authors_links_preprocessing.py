import random
import math
import pandas as pd
import numpy as np
import requests
import os
import time
import re
import copy
import cv2
import wget
import urllib
import skimage.metrics as skm
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import html


mds = pd.read_csv('./authorslinks_tmp.csv')
urls = mds.URL.unique()
au = mds.Authors.unique()

print(len(urls))
print(len(au))

#my_dataset = pd.read_excel('./new_dataset_2.xlsx', engine='openpyxl')

my_dataset = pd.read_csv('./current_ds.csv') #dataset for new features

authors = my_dataset.Author.unique()

dic = {}

def normalize_word(word):
    new_word = unidecode(word.lower()).replace('\\','').replace('\'','')
    return new_word

def find_author_page(author):
    #url for searching author page
    if art_author in dic:
        return dic[art_author]

    url = 'https://www.wikiart.org/en/Search/' + author

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path=r'./chromedriver.exe', options=options)
    driver.get(url)
    time.sleep(2)

    if 'Sorry, nothing found' in driver.page_source:
            driver.quit()
            return ''

    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    author_info = soup.find('div', {'class' : 'artist-name'})

    author_link = ''

    if author_info:
        author_link = author_info.find('a', {'class' : 'ng-binding'})
        if author_link:
            author_link = author_link.get('href')
    else:
        author_link = ''

    driver.quit()
    
    del soup
    return author_link

cnt = 0

for i in authors:
    art_author = normalize_word(i)
    
    url = find_author_page(art_author)

    dic[art_author] = url

    if url == '':
        print(i, "no success")
    else:
        print(i, "success")
        cnt = cnt + 1

print(cnt)

df = pd.DataFrame(list(dic.items()), columns=['Authors', 'URL'])
df.to_csv('./authorslinks_tmp.csv', index =False)
