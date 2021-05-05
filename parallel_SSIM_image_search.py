import argparse
import collections
import math
import multiprocessing
import os
import sys
import requests
import cv2
import pandas as pd
import numpy as np
import skimage.metrics as skm
import random
import math
import time
import re
import copy
import wget
import urllib
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import html


def main():
    my_dataset = pd.read_csv('path to/test_dataset.csv')
    images = pd.read_csv('path to/wikiart_masks.csv')
    arts_features = ('Original Title', 'Date', 'Style', 'Period', 'Genre', 'Media', 'Location', 'Wikipedia article', 'References', 'Wikiart art url', 'Wikiart image url')

    source = list(zip(images['mask'], range(len(images['mask']))))
    concurrency = 8

    n = len(my_dataset) #arts number

    for i in range(n):
        target = my_dataset.iloc[i, 23]

        if(type(target) == float):
            if(math.isnan(target)):
                print(i, "success")
                continue
        
        try:
            targetImage = download_image(target)
        except:
            print(i, "success")
            continue
        
        summary = scale(source, targetImage, concurrency)

        answer = 0
        ans_val = -1
        for val, num in summary:
            if(ans_val < val):
                answer = num
                ans_val = val


        if(ans_val < 0.7):
            url = ''
        else:
            url = images.iloc[answer, 1]

        if url == '' or url == 'https://www.wikiart.org':
            print(i, "success")
            continue

        try:
            text = requests.get(url).text
            soup = BeautifulSoup(text, "lxml")
        except:
            continue

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
        if image_url != None:
            valid_image_url = (image_url.__repr__()).split('"')[1]
            my_dataset['Wikiart image url'][i] = valid_image_url

        art_info_t = soup.find('article')
        art_info_t2 = None
        
        if art_info_t != None:
            art_info_t2 = art_info_t.find('ul')
            if art_info_t2 != None:
                art_info = art_info_t2.find_all('li')

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
    my_dataset.to_excel('path to/new_dataset_3.xlsx')
    my_dataset.to_csv('path to/test_dataset.csv', index =False)


def scale(processes, source, target, concurrency):
    canceled = False
    jobs = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    if(processes == []):
        processes = create_processes(jobs, results, concurrency)
    todo = add_jobs(source, target, jobs)
    
    try:
        jobs.join()
    except KeyboardInterrupt: # May not work on Windows
        canceled = True

    result = []
    while not results.empty(): # Safe because all jobs have finished
        result.append(results.get_nowait())

    return result, processes

def scale(source, target, concurrency):
    canceled = False
    jobs = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    processes = create_processes(jobs, results, concurrency)
    todo = add_jobs(source, target, jobs)
    
    try:
        jobs.join()
    except KeyboardInterrupt: # May not work on Windows
        canceled = True

    result = []
    while not results.empty(): # Safe because all jobs have finished
        result.append(results.get_nowait())

    for p in processes:
        p.terminate()

    return result

def create_processes(jobs, results, concurrency):
    processes = []
    for _ in range(concurrency):
        process = multiprocessing.Process(target=worker, args=(jobs, results))
        process.daemon = True
        process.start()
        processes.append(process)
    return processes

def worker(jobs, results):
    while True:
        try:
            source, targetImage = jobs.get()
            sourceImage, number = source
            
            try:
                result = diff_one(sourceImage, targetImage)
                results.put((result, number))
            except:
                Exception()
        finally:
            jobs.task_done()


def add_jobs(source, target, jobs):
    todo = 0
    for name in source:
        todo += 1
        sourceImage = name
        targetImage = target
        jobs.put((sourceImage, targetImage))
    return todo


def download_image(image_link):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    'ACCEPT-ENCODING' : 'gzip, deflate, br',
    'ACCEPT-LANGUAGE' : 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'REFERER' : 'https://www.google.com/'
    }

    sz = 50

    img = requests.get(image_link, headers = headers)
    name = ".\img" + time.time().__repr__() + ".jpg"

    out = open(name, "wb")
    out.write(img.content)
    out.close()    

    image = cv2.imread(name)
    resized = cv2.resize(image, (sz, sz), interpolation = cv2.INTER_AREA) 
    gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    
    os.remove(name)

    return gray_image


def str_to_ds(str):
    values = str.split(',')

    values = values[:-1]

    new_values = [int(x) for x in values]
    
    new_values = [new_values[i:i + 50] for i in range(0, len(new_values), 50)]

    ds = np.array(new_values, dtype=np.uint8)

    return ds


def diff_one(sourceImage, targetImage):
    try:
        gray_image1 = targetImage
        gray_image2 = str_to_ds(sourceImage)        
    except Exception:
        return -1

    result = skm.structural_similarity(gray_image1, gray_image2)
    return result


if __name__ == "__main__":
    main()
