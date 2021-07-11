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
import pickle
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import html

def compare(image_name1, image_name2):
    sz = 50
    image1 = cv2.imread(image_name1)
    resized_ssim_1 = cv2.resize(image1, (sz,sz), interpolation = cv2.INTER_AREA)
    gray_image_ssim_1 = cv2.cvtColor(resized_ssim_1, cv2.COLOR_BGR2GRAY)

    image2 = cv2.imread(image_name2)
    resized_ssim_2 = cv2.resize(image2, (sz,sz), interpolation = cv2.INTER_AREA)
    gray_image_ssim_2 = cv2.cvtColor(resized_ssim_2, cv2.COLOR_BGR2GRAY)

    mssim = skm.structural_similarity(gray_image_ssim_1, gray_image_ssim_2)

    hist_1 = cv2.calcHist([image1], [0,1,2], None, [16,16,16],[0,256,0,256,0,256])
    hist_1 = cv2.normalize(hist_1, hist_1).flatten()

    hist_2 = cv2.calcHist([image2], [0,1,2], None, [16,16,16],[0,256,0,256,0,256])
    hist_2 = cv2.normalize(hist_2, hist_2).flatten()


    similarity=cv2.compareHist(hist_1, hist_2, cv2.HISTCMP_INTERSECT)
    normal_sim=cv2.compareHist(hist_1, hist_1, cv2.HISTCMP_INTERSECT)

    print("Normal similarity: ", normal_sim)
    print("Hist similarity: ", similarity)
    print("SSIM: ", mssim)

# compare("2.1.jpg", "2.2.jpg")
# compare("1.1.jpg", "1.2.jpg")
# compare("5.jpg", "6.jpg")