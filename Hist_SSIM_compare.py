import random
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
from sklearn.neighbors import NearestNeighbors
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from lxml import html
from PIL import Image


def compare(image_name1, image_name2):
    sz = 50
    image1 = cv2.imread(image_name1)
    
    a,b,c = image1.shape 

    v_diff = a // 11
    h_diff = b // 11

    a = a - v_diff
    b = b - h_diff
    image1 = image1[v_diff: a, h_diff: b]

    resized_ssim_1 = cv2.resize(image1, (sz,sz), interpolation = cv2.INTER_AREA)
    gray_image_ssim_1 = cv2.cvtColor(resized_ssim_1, cv2.COLOR_BGR2GRAY)

    image2 = cv2.imread(image_name2)

    a,b,c = image2.shape 

    v_diff = a // 11
    h_diff = b // 11

    a = a - v_diff
    b = b - h_diff
    image2 = image2[v_diff: a, h_diff: b]

    resized_ssim_2 = cv2.resize(image2, (sz,sz), interpolation = cv2.INTER_AREA)
    gray_image_ssim_2 = cv2.cvtColor(resized_ssim_2, cv2.COLOR_BGR2GRAY)

    mssim = skm.structural_similarity(gray_image_ssim_1, gray_image_ssim_2)

    histSize = 16
    hist_1 = cv2.calcHist([image1], [0,1,2], None, [histSize,histSize,histSize],[0,256,0,256,0,256])
    hist_1 = cv2.normalize(hist_1, hist_1).flatten()

    hist_2 = cv2.calcHist([image2], [0,1,2], None, [histSize,histSize,histSize],[0,256,0,256,0,256])
    hist_2 = cv2.normalize(hist_2, hist_2).flatten()

    images = [image1, image2]

    plt.figure(figsize = (18, 5))
    
    for i in range(2):
        plt.subplot(1, 2, i + 1)

        color = ('b','g','r')
        for j,col in enumerate(color):
            hist = cv2.calcHist([images[i]],[j], None,[256],[0,256])
            plt.plot(hist, color = col)
            plt.xlim([0,256])

    plt.show()

    similarity = cv2.compareHist(hist_1, hist_2, cv2.HISTCMP_INTERSECT)
    normal_sim = cv2.compareHist(hist_1, hist_1, cv2.HISTCMP_INTERSECT)

    print("Normal similarity: ", normal_sim)
    print("Hist similarity: ", similarity)
    print("SSIM: ", mssim)

    print(similarity / normal_sim * 100)


def knn_hists_query(image_name, folder_name):
    histSize = 16
    
    query_image=cv2.imread(image_name)
    query_hist_combined=cv2.calcHist([query_image],[0,1,2],None,[histSize,histSize,histSize],[0,256,0,256,0,256])
    query_hist_combined = cv2.normalize(query_hist_combined, query_hist_combined).flatten()

    files = os.listdir(folder_name)
    
    hists = []

    for file_name in files:
        img = cv2.imread(f'{folder_name}/{file_name}')


        hist_combined = cv2.calcHist([img],[0,1,2],None,[histSize,histSize,histSize],[0,256,0,256,0,256])
        hist_combined = cv2.normalize(hist_combined, hist_combined).flatten()
        
        hists.append({"hist":hist_combined,"file_name":file_name})

    knn = NearestNeighbors(n_neighbors=10,algorithm='brute',metric='euclidean')
    
    hists_list = list(map(lambda el: el['hist'], hists))
    knn.fit(hists_list)

    distances, indices = knn.kneighbors([query_hist_combined], return_distance = True)

    indices = indices[0]

    for idx in indices:
        print(f'{folder_name}/{files[idx]}')    

if __name__ == "__main__":
    #compare("2.1.jpg", "2.2.jpg")
    #compare("1.1.jpg", "1.2.jpg")

    #same
    #compare("5.jpg", "6.jpg")
    #compare("6.jpg", "crop_7.jpg")
    #compare("5.jpg", "7.jpg")
    #compare("8.jpg", "9.jpg")

    #different
    #compare("01.jpg", "1.1.jpg")
 

    #knn_hists_query("1.1.jpg", "./images")
    #knn_hists_query("5.jpg", "./images")
    knn_hists_query("9.jpg", "./images")
