#!/usr/bin/env python3 

import sys
import re
import os
import pymysql
import numpy as np
import pandas as pd
import logging
import traceback
import time
import random
import requests
from bs4 import BeautifulSoup  
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Automate:

    _connection = None

    @staticmethod
    def _get_db_connection(dbname):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='h3llo2u',
            db=dbname
            )


    @classmethod
    def make_connection(cls):
        cls._connection = cls._get_db_connection('hotels')


    @staticmethod
    def dataset_as_list(rows):
        # each record is in the form of dict
        # list will contain all the records
        data = pd.read_csv('cleartrip_hotels.csv')
        final_list = []
        if rows==0:
            pdDict =  data.to_dict()
            size = data.shape[0]
        else:
            pdDict =  data.head(rows).to_dict()
            size = rows
        record=0
        while 1:
            if record==size:
                break
            hotel = {}
            for attr, colInfo in pdDict.items():
                hotel[attr] = colInfo[record]
            final_list.append(hotel)
            record+=1
        return final_list

    @staticmethod
    def read_dataset(rows=0):
        return Automate.dataset_as_list(rows)

    def insert_hotels_to_database(self, rows):
        # data is in the form of list
        # rows is the row count
        data = Automate.read_dataset(rows)
        counter=0
        while counter<len(data):
            hotel = data[counter]
            # print(str(hotel['property_id']), hotel['property_name'])
            # hotel is a dict
            Automate.insertHotel(str(hotel['property_id']), hotel['property_name'])
            counter+=1

    def insertHotel(p_id, p_name):
        with Automate._connection:
            cursor = Automate._connection.cursor()
            sql = "INSERT INTO `main_info` (`property_id`, `property_name`) VALUES (%s, %s)"
            try:
                if cursor.execute(sql, (p_id, p_name))==1:
                    print("Added to database, hotel = "+p_name+", hotel_id = "+p_id)
            except Exception as e:
                logging.error(traceback.format_exc())


    def update_data(self, rows):
        data = Automate.read_dataset(rows)
        counter=0
        while counter<len(data):
            hotel = data[counter]
            # print(str(hotel['property_id']), hotel['property_name'])
            # hotel is a dict
            Automate.updateHotel(str(hotel['property_id']), hotel)
            counter+=1


    def insert_review_ratings(self, rows):
        data = Automate.read_dataset(rows)
        counter=0
        c=0
        while counter<len(data):
            hotel = data[counter]
            # print(str(hotel['property_id']), hotel['property_name'])
            # hotel is a dict
            strr = hotel['tad_stay_review_rating']
            rat = None
            if str(strr)!='nan':
                try:
                    types = strr.split('|')
                    rat = [str(types[x])[-3:] for x in range(6)]
                    if rat is not None:
                        Automate.insert_rating(str(hotel['property_id']), rat)
                        c+=1
                except IndexError as e:
                    pass
            counter+=1
        print(c)

    def insert_rating(id, ratings):
        if len(str(ratings))<=0:
            return

        with Automate._connection:
            cursor = Automate._connection.cursor()
            sql = "INSERT INTO `hotel_stay_review_rating` (`property_id`, `location`, `rooms`, `services`, `value`, `cleanliness`, `sleep_quality` ) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            try:
                if cursor.execute(sql, (id, ratings[0], ratings[1], ratings[2], ratings[3], ratings[4], ratings[5]))==1:
                    print("Added to database, hotel = "+id)
            except Exception as e:
                logging.error(traceback.format_exc())


    def randomize_rating_count(hotels):
        for h in hotels:
            if str(h['tad_review_count'])!='nan':
                for _ in range(int(h['tad_review_count'])):
                    rating = [str(h['property_id']), str(random.randint(int(h['tad_review_rating']-1), 5))]
                    Automate.insert_rating_count(rating[0], rating[1])
            else:
                for _ in range(random.randint(1, 50)):
                    rating = [str(h['property_id']), str(random.randint(0, 5))]
                    Automate.insert_rating_count(rating[0], rating[1])


    def insert_rating_count(id, rating):
        # print(rating[0], rating[1])
        # return
        if len(id)<=0 or len(rating)<=0:
            return

        with Automate._connection:
            cursor = Automate._connection.cursor()
            sql = "INSERT INTO `hotel_ratings` (`property_id`, `rating`) VALUES (%s, %s)"
            try:
                if cursor.execute(sql, (id, rating))==1:
                    print("Added to hotel_ratings, hotel = "+id)
            except Exception as e:
                logging.error(traceback.format_exc())
            cursor.close()


    def insert_images(self):
        data = Automate.read_dataset(0)
        counter=0
        while counter<len(data):
            try:
                hotel = data[counter]
                # print(str(hotel['property_id']), hotel['property_name'])
                # hotel is a dict
                urls = hotel['image_urls'].split('|')
                if len(urls)<=0:
                    counter+=1
                    continue
                for url in urls:
                    Automate.insert_image_url(str(hotel['property_id']), url)
                counter+=1
            except Exception as e:
                counter+=1
                logging.error(traceback.format_exc())

    def insert_image_url(id, url):
        if len(str(url))<=0:
            return
        cursor = Automate._connection.cursor()
        with Automate._connection:
            
            sql = "INSERT INTO `hotel_images` (`property_id`, `property_image_url`) VALUES (%s, %s)"
            try:
                if cursor.execute(sql, (id, url))==1:
                    print("Added to database, hotel = "+id+", hotel_id = "+url)
            except Exception as e:
                logging.error(traceback.format_exc())
        cursor.close()

    def updateImageUrl(self):
        data = Automate.read_dataset(0)
        counter=0
        while counter<len(data):
            try:
                cursor = Automate._connection.cursor()
                hotel = data[counter]
                # print(str(hotel['property_id']), hotel['property_name'])
                # hotel is a dict
                urls = hotel['image_urls']
                hid = str(hotel['property_id'])
                with Automate._connection:
                    sql = "UPDATE `main_info` SET `image_urls`=%s WHERE `property_id` = %s"
                    try:
                        if cursor.execute(sql, (urls, hid))==1:
                            print("hotel updated=", "hotel_id = "+ hid)
                            counter+=1
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        counter+=1
                cursor = Automate._connection.cursor()                
            except Exception as e:
                counter+=1
                cursor = Automate._connection.cursor()
                logging.error(traceback.format_exc())

    @classmethod
    def fireQuery(cls, sql, fetch=False):
        result = 0
        try:
            cursor = Automate._connection.cursor()
            with Automate._connection:
                if fetch==True:
                    cursor.execute(sql)
                    result = cursor.fetchall()
                else:
                    if cursor.execute(sql)==1:
                        result=1
        except Exception as e:
            cursor.close()
            logging.error(traceback.format_exc())   
        cursor.close()
        return result

    def updateRatingCount(self):
        sql = "SELECT `property_id` as pid, COUNT(*) as c FROM `hotel_ratings` GROUP BY `property_id`"
        rating_data = Automate.fireQuery(sql, fetch=True)
        # print(rating_data)
        for rating in rating_data:
            # print(rating)
            sql = "UPDATE `main_info` SET `rating_count` ="+str(rating[1])+" WHERE `property_id` = "+rating[0]
            print(Automate.fireQuery(sql))


    def insertRatingCount(self):
        sql = "SELECT `property_id` as pid, COUNT(*) as c FROM `hotel_ratings` GROUP BY `property_id`"
        rating_data = Automate.fireQuery(sql, fetch=True)
        # print(rating_data)
        for rating in rating_data:
            print(rating)
            # continue
            sql = "INSERT INTO `hotel_ratings_count` (`property_id`, `rating_count`) VALUES ("+str(rating[0])+","+str(rating[1])+")"
            print(Automate.fireQuery(sql))
    

    def updateAvgRating(self):
        sql = "SELECT `property_id` AS pid, AVG(`rating`) AS avg_rating FROM `hotel_ratings` GROUP BY `property_id`"
        avg_ratings = Automate.fireQuery(sql, fetch=True)

        # print(avg_ratings)

        for avgr in avg_ratings:
            # print(avgr[0], avgr[1])
            sql = "UPDATE `main_info` SET `tad_review_rating` ="+str(avgr[1])+" WHERE `property_id` = "+avgr[0]
            print(Automate.fireQuery(sql))

    def updatePrices(self):
        sql = "SELECT `property_id`, `rating_count` FROM `main_info`"
        data = Automate.fireQuery(sql, fetch=True)
        p = []
        for hotel in data:
            rc = hotel[1]
            price = 500
            if int(rc) > 100 and int(rc)<400:
                price = random.randint(1500, 3000)
                # print(rc, price)
            elif int(rc) > 400 and int(rc)<1000:
                price = random.randint(3000, 5000)
                # print(rc, price)
            elif int(rc) > 1000 and int(rc)<1500:
                price = random.randint(5000, 7000)
                # print(rc, price)
            elif int(rc) > 1500:
                price = random.randint(8000, 10000)
                # print(rc, price)
            else:
                price = random.randint(500, 1000)
                # print(rc, price)
            sql = "UPDATE `hotel_ratings_count` SET `price` ="+str(price)+" WHERE `property_id` = "+hotel[0]
            if Automate.fireQuery(sql)==1:
                print("hotel_id = "+hotel[0])

            # h = tuple([rc, price])
            # p.append(h)
        # print(p)



        # for avgr in avg_ratings:
        #     # print(avgr[0], avgr[1])
        #     sql = "UPDATE `main_info` SET `tad_review_rating` ="+str(avgr[1])+" WHERE `property_id` = "+avgr[0]
        #     print(Automate.fireQuery(sql))



    
    def updateHotel(id, hotel):
        city = hotel['city']
        province = hotel['province']
        area = ascii(hotel['area'])
        state = hotel['state']
        address = hotel['address']
        hotel_description = ascii(hotel['hotel_description'])
        room_count = hotel['room_count']
        room_type = hotel['room_type']
        tad_review_rating = hotel['tad_review_rating']

        print(hotel['image_urls'])
        return

        if str(area)=='nan':
            return 

        # if str(tad_review_rating)=='nan':
        #     tad_review_rating=round(random.uniform(2, 5), 1)

        with Automate._connection:
            cursor = Automate._connection.cursor()
            sql = "UPDATE `main_info` SET `area`=%s WHERE `property_id` = %s"
            try:
                if cursor.execute(sql, (area, id))==1:
                    print("hotel updated=", "hotel_id = "+ id)
            # sql = "UPDATE `main_info` SET `city`=%s, `province`=%s, `area`=%s, `state`=%s, `address`=%s, `hotel_description`=%s, `room_count`=%s, `room_type`=%s, `tad_review_rating`=%s WHERE `property_id` = %s"
            # try:
            #     if cursor.execute(sql, (city, province, area, state, address, hotel_description, room_count, room_type, tad_review_rating, id))==1:
            #         print("hotel updated=", "hotel_id"+ id)
            except Exception as e:
                logging.error(traceback.format_exc())


    @classmethod
    def readHotels(cls):
        with cls._connection.cursor() as cursor:
            sql = "SELECT * FROM `main_info`"
            cursor.execute(sql)
            result = cursor.fetchall()
        return result

    @classmethod
    def readHotelRatings(cls):
        with cls._connection.cursor() as cursor:
            sql = "SELECT * FROM `hotel_ratings`"
            cursor.execute(sql)
            result = cursor.fetchall()
        return result

    def getlastcounter(self, id):
        hotels = Automate.read_dataset()
        counter=0
        for h in hotels:
            if h['property_id']==id: 
                return counter
            counter+=1
        return counter

    def insert_reviews_text():
        hotels = Automate.read_dataset()
        counter = 3965
        fp = webdriver.FirefoxProfile('/home/tarun/.mozilla/firefox/ucmtt9p9.default')
   
        for h in hotels[counter:]:
            hotel_id = str(h['property_id'])
            if len(str(h['pageurl']))<=0:
                continue
            try:
                driver = webdriver.Firefox(fp)
                driver.implicitly_wait(10)
                rc, reviews = Automate.get_reviews_list(str(h['pageurl']), driver)
                cursor = Automate._connection.cursor()
                for review in reviews:
                    with Automate._connection:
                        sql = "INSERT INTO `hotel_reviews` (`property_id`, `property_reviews`) VALUES (%s, %s)"
                        try:
                            if cursor.execute(sql, (hotel_id, review))==1:
                                print("Added to database, hotel = "+hotel_id)
                        except Exception as e:
                            logging.error(traceback.format_exc())
                            driver.close()

                    sql = "UPDATE `main_info` SET `tad_review_count`=%s WHERE `property_id` = %s"
                try:
                    if cursor.execute(sql, (rc, hotel_id))==1:
                        print("hotel updated=", "hotel_id = "+ hotel_id+" counter = "+str(counter))
                except Exception as e:
                    logging.error(traceback.format_exc())
                    driver.close()
                cursor.close() 
                driver.close()
            except Exception as e:
                logging.error(traceback.format_exc())
                driver.close()
            time.sleep(5)
            counter+=1

    @classmethod
    def get_reviews_list(cls, page_url, driver):
        # url="https://www.cleartrip.com/hotels/details/"+str(hotel_id)
        url = page_url
        driver.get(url)
        html_source = driver.page_source   
        soup = BeautifulSoup(html_source, 'html.parser')
        rc = str(soup.find_all('a', {"class":"reviewLink"})[0])
        reviewcount = re.sub('<a class="reviewLink" href="#taReviews">', '', rc)
        reviewcount = re.sub('</a>', '', reviewcount)
        reviewcount = re.sub('reviews', '', reviewcount)
        reviewcount = reviewcount.lstrip()
        reviewcount = reviewcount.rstrip()
        malreviews = soup.find_all('p', { "class" : "truncateReviewText"})
        reviews = []
        for ml in malreviews:
            ml  = str(ml)
            r = re.sub('<p class="truncateReviewText">', '', ml)
            r = re.sub('</p>', '', r)
            r = r.lstrip()
            r = r.rstrip()
            reviews.append(ascii(r))
        return tuple([reviewcount, reviews])

    def insert_room_facility(self):
        hotels = Automate.read_dataset()
        cols = ['Toiletries', 'Bedside Lamp', 'Luggage Rack', 'Air Conditioning', 'Television', 'Internet / Broadband', 'Telephone', 'Refrigerator', 'Free Wi-Fi', 'Mini Bar', 'Room Heater', 'Writing Desk / Study Table', 'Wake-Up Call Service']
        # for h in hotels:
        #     hotel_id = str(h['property_id'])
        #     sql = "INSERT INTO `room_facilities` (`property_id`) VALUES (%s)"
        #     with Automate._connection:
        #         try:
        #             if cursor.execute(sql, (hotel_id))==1:
        #                 print("hotel inserted=", "hotel_id = "+ hotel_id)
        #         except Exception as e:
        #             logging.error(traceback.format_exc())
        # cursor.close()
        # return
        cursor = Automate._connection.cursor()
        for h in hotels:
            facilities = str(h['room_facilities']).split('|')
            hotel_id = str(h['property_id'])
            for f in facilities:
                fac = f.strip()
                if fac in cols:
                    sql = "UPDATE `room_facilities` SET `"+fac+"`=%s WHERE `property_id` = %s"
                    with Automate._connection:
                        try:
                            if cursor.execute(sql, ('1',hotel_id))==1:
                                print("hotel updated=", "hotel_id = "+ hotel_id)
                        except Exception as e:
                            logging.error(traceback.format_exc())
