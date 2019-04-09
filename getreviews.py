#!/usr/bin/env python3 

import sys
import requests
from bs4 import BeautifulSoup  
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import os

def main():

    def get_reviews_list(hotel_id):
        url="https://www.cleartrip.com/hotels/details/"+hotel_id
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        driver.get(url)
        html_source = driver.page_source   
        soup = BeautifulSoup(html_source, 'html.parser')
        malreviews = soup.find_all('p', { "class" : "truncateReviewText"})
        reviews = []
        for ml in malreviews:
            ml  = str(ml)
            r = re.sub('<p class="truncateReviewText">', '', ml)
            r = re.sub('</p>', '', r)
            r = r.lstrip()
            r = r.rstrip()
            reviews.append(r)
        return review



if __name__ == "__main__":
    main()


