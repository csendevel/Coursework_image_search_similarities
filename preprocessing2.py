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
import json
import skimage.metrics as skm
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import html
from pprint import pprint


def find_art_page(art, art_year):
    #url for searching art page
    url = 'https://www.wikiart.org/en/Search/' + art

    try:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(executable_path=r'./chromedriver.exe', options=options)
        driver.get(url)
        time.sleep(1)

        if 'Sorry, nothing found' in driver.page_source:
                driver.quit()
                return ''

        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        art_name_info = soup.find_all('a', {'class' : 'artwork-name ng-binding'})
        art_year_info = soup.find_all('span', {'class' : 'artwork-year ng-binding'})

        art_link = ''
        for (art, year) in zip(art_name_info, art_year_info): 
            if art_year == year.text or art_year == 'none':
                art_link = art.get('href')
            
        driver.quit()
        
        del soup

    except:
        return ''

    return art_link


def image_processing(image):
    sz = 50
    try:
        _image = cv2.imread(image)

        #deleting white border
        ##

        resized = cv2.resize(_image, (sz, sz), interpolation = cv2.INTER_AREA) 
        gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        string = ""
        for i in gray_image:
            for j in i:
                string = string + j.__repr__() + ","

    except:
        return ''

    return string

mds = pd.read_csv('./wikiart-dataset/wikiart/wclasses.csv')

l = len(mds)
n = 16000

#my_dataset = pd.DataFrame({"art":pd.Series(['']*l), "link": pd.Series(['']*l), "mask": pd.Series(['']*l) })
l = 21000

my_dataset = pd.read_csv('./wikiart_masks.csv')

#print(my_dataset)

for i in range(n, l):
    art = mds.iloc[i, 0].split('/')[1]
    folder = mds.iloc[i, 0].split('/')[0]

    art = art.replace('_',' ').replace('-',' ')[0:-4]
    
    year = 'none'
    if art[-4:].isdigit():
        year = art[-4:]
        art = art[:-4]

    url = find_art_page(art, year)

    current_path_to_art = "./wikiart-dataset/wikiart/" + mds.iloc[i, 0]

    art_mask = image_processing(current_path_to_art)

    my_dataset['art'][i] = art
    my_dataset['link'][i] = 'https://www.wikiart.org' + url
    my_dataset['mask'][i] = art_mask

    print(i)

my_dataset.to_csv('./wikiart_masks.csv', index =False)