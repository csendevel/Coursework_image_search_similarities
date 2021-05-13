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

my_dataset = pd.read_csv('./wikiart_masks.csv') #dataset for new features


def str_to_ds(str):
    values = str.split(',')

    values = values[:-1]

    new_values = [int(x) for x in values]
    
    new_values = [new_values[i:i + 50] for i in range(0, len(new_values), 50)]

    ds = np.array(new_values, dtype=np.uint8)

    return ds

def image_processing(image):
    sz = 50
    try:
        _image = cv2.imread(image)

        resized = cv2.resize(_image, (sz, sz), interpolation = cv2.INTER_AREA) 
        gray_image = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    except:
        return ''

    return gray_image


def find_image(source):
    tmp = -2
    ans = ''
    for i in range(len(my_dataset)):
        image_mask = my_dataset.iloc[i, 2]
        
        if(type(image_mask) == float):
            if(math.isnan(image_mask)):
                continue

        new_image = str_to_ds(image_mask)

        mssim = skm.structural_similarity(source, new_image)
        if mssim > tmp:
            tmp = mssim
            #print(tmp)
            ans = my_dataset.iloc[i, 1]

    return (ans, tmp)

image = input()
ds = image_processing(image)
(url, mssim) = find_image(ds)

if(mssim >= 0.8): 
    print(url)
else:
    print("image not found")
