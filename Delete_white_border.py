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


def delete_white_border(image_name):
    sz = 50
    image =  cv2.imread(image_name)

    cropped = []

    white = [255, 255, 255]

    flag = False
    up_border = 0 
    for i in range(len(image)):
        for j in image[i]:
            if (list(j) != white):
                up_border = i
                flag = True
                break
        if(flag): 
            break


    flag = False
    down_border = 0
    for i in range(len(image) - 1, -1, -1):
        for j in image[i]:
            if (list(j) != white):
                down_border = i
                flag = True
                break
        if(flag): 
            break

    flag = False
    left_border = 0 
    for j in range(len(image[0])):
        for i in range(len(image)):
            if (list(image[i][j]) != white):
                left_border = j
                flag = True
                break
        if(flag): 
            break

    flag = False
    right_border = 0 
    for j in range(len(image[0]) - 1, -1, -1):
        for i in range(len(image)):
            if (list(image[i][j]) != white):
                right_border = j
                flag = True
                break
        if(flag): 
            break

    cropped = image[up_border:down_border, left_border:right_border]

    cv2.imwrite("crop_image.jpg", cropped)

image = input()
delete_white_border(image)