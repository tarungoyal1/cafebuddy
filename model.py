from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
import pymysql
import numpy as np
import pandas as pd
import sklearn
from datetime import datetime
import logging
import traceback
from sklearn.neighbors import NearestNeighbors

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(250))

    def __init__(self, firstname, lastname, email, passwd):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(passwd)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Hotel:

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


    @classmethod
    def fireQuery(cls, sql, fetch=False):
        result = 0
        try:
            cursor = Hotel._connection.cursor()
            with Hotel._connection:
                if fetch==True:
                    cursor.execute(sql)
                    # to get dict of col:value rather than bland tuple
                    columns = [col[0] for col in cursor.description]
                    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    result = rows
                else:
                    if cursor.execute(sql)==1:
                        result=1
        except Exception as e:
            cursor.close()
            logging.error(traceback.format_exc())   
        cursor.close()
        return result

    def getHotelInfo(self, hid):
        sql = "SELECT * FROM `main_info` WHERE `property_id`="+str(hid)
        hoteldata = Hotel.fireQuery(sql, True)
        return hoteldata

    def getHotelDesc(self, hid):
        sql = "SELECT * FROM `hotel_desc` WHERE `property_id`="+str(hid)
        hoteldata = Hotel.fireQuery(sql, True)
        return hoteldata

    @classmethod    
    def getHotelRatingCount(self, hid):
        sql = "SELECT `rating_count` FROM `hotel_ratings_count` WHERE `property_id`="+str(hid)
        hoteldata = Hotel.fireQuery(sql, True)
        return hoteldata

    @classmethod
    def getRoomFacilities(cls, hid):
        sql = "SELECT * FROM `room_facilities` WHERE `property_id`="+str(hid)
        hoteldata = Hotel.fireQuery(sql, True)
        return hoteldata

    @classmethod
    def getAvailableFacilities(cls, hid):
        sql = "SELECT * FROM `room_facilities` WHERE `property_id`="+str(hid)
        hoteldata = Hotel.fireQuery(sql, True)[0]
        availfac = []
        for col,val in hoteldata.items():
            if hoteldata[col]=='1':
                availfac.append(col)
        return availfac

    @classmethod
    def readHotels(cls, ids):
        idstring = ""
        for i in ids:
            idstring += str("'"+i+"', ")
        values = str(idstring[:-2])
        sql = "SELECT * FROM `main_info` WHERE `property_id` IN ("+values+")"
        result = Hotel.fireQuery(sql, True)
        return result




class PopularHotels:

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

    @classmethod
    def readHotels(cls, ids):
        idstring = ""
        for i in ids:
            idstring += str("'"+i+"', ")
        values = str(idstring[:-2])
        # print(values)
        with cls._connection.cursor() as cursor:
            sql = "SELECT * FROM `main_info` WHERE `property_id` IN ("+values+")"
            cursor.execute(sql)
            result  = cursor.fetchall()

            # to get the data as list containing a dict with colname, value
            # columns = [col[0] for col in cursor.description]
            # rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return result

    @classmethod
    def getHotelImageUrls(cls, id):
        with cls._connection.cursor() as cursor:
            sql = "SELECT * FROM `hotel_images` WHERE `property_id`="+id
            cursor.execute(sql)
            result  = cursor.fetchall()
        return result

    @classmethod
    def getPopularHotels(cls, city, offset=0, count=5):
        hotels = pd.read_csv("hotel_ratings_city.csv")
        myhotels = hotels.loc[hotels['city'] == city]
        popular_hotels = myhotels.groupby('property_id')['rating'].count().sort_values(ascending=False)
        sliced = popular_hotels[offset:offset+count]
        hotels_dict = sliced.to_dict()

        # now hotels_dict has hotel_id and rating count for each hotel
        #but we need extra information about the hotel

        hotels_sorted = []
        final_hotels_sorted = []

        idslist = []
        for hotel in hotels_dict:
            idslist.append(str(hotel))
        hotels_info  = list(PopularHotels.readHotels(idslist))

        for i in idslist:
            ratingcount = hotels_dict[int(i)]
            # print(ratingcount)
            for h in hotels_info:
                if h[1]==i:
                    hotels_sorted.append(h)
                    hotels_info.remove(h)
                    break

        # print(hotels_sorted)
        cols = ['hid', 'property_id', 'property_name', 'city', 'province', 'area', 'state', 'address', 'image_urls', 'room_count', 'room_type','tad_review_rating', 'tad_review_count', 'rating_count']
        for hotel in hotels_sorted:
            # take attributes that you need
            h = {cols[i]:hotel[i] for i in range(14)}
            h['string_rating_count'] = str(hotel[13])
            final_hotels_sorted.append(h)

        return final_hotels_sorted

class RecommendHotels(Hotel):

    @classmethod
    def parseFacilities(cls, curhid):
        # fac is a list containing dict as only one element
        fac = Hotel.getRoomFacilities(curhid)
        ratingcount = Hotel.getHotelRatingCount(curhid)
        # print("-----"+str(ratingcount)+"---")
        binfac = []
        for v in fac[0].values():
            binfac.append(int(v))
        binfac.append(int(ratingcount[0]['rating_count']))
        return binfac[2:]



    def recommendUsingKNN(self, curhid, city, count=8):
        hotels = pd.read_csv("main_info_full.csv")
        ratings = pd.read_csv("hotel_ratings_count.csv")
        room_fac_df = pd.read_csv("hotel_room_facilities.csv")


        myratings = ratings.loc[ratings['city'] == city]
        myhotels = hotels.loc[hotels['city'] == city]

        partial_combined = pd.merge(myhotels, room_fac_df, on='property_id')
        fully_combined = pd.merge(partial_combined, myratings, on='property_id')
        final = fully_combined.iloc[:, [1,3]+[x for x in range(12, 27) if x!=25]]
    
        current_fac = RecommendHotels.parseFacilities(curhid)
        
        X = final.iloc[:, [c for c in range(2, 16)]].values
        # print(current_fac)
        
        # Build the nearest neighbors model by using NearestNeighbors object and passing n_neighbors=1
        neighbors = NearestNeighbors(n_neighbors=count).fit(X)
        
        #to find the nearest neighbor(s), we call kneighbors function and pass our test(test point) as arg

        nbrs = neighbors.kneighbors([current_fac])[1][0]

        nbrs_hids = [str(final.iloc[n][0]) for n in nbrs]
        print(nbrs_hids)
        try:
             nbrs_hids.remove(curhid)
        except Exception as e:
            pass

        nbrs_hotels_data = Hotel.readHotels(nbrs_hids)

        return nbrs_hotels_data

class TrackActivity(Hotel):


    def recordActivity(self, uid, hid, city):
        # Insert a new record
        h = Hotel()
        h.make_connection()
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO `user_history` (`user_id`, `visited_hotel_id`, `visited_city`, `visit_timestamp`) VALUES("+str(uid)+", '"+hid+"', '"+city+"', '"+t+"')"
        result = Hotel.fireQuery(sql, False)
        return result

    def getUserActivity(self, uid):
        h = Hotel()
        h.make_connection()
        sql = "SELECT `visited_hotel_id`, MAX(`visit_timestamp`) AS `visit_timestamp`, `main_info`.`city` FROM `user_history` INNER JOIN `main_info` ON `user_history`.`visited_hotel_id` = `main_info`.`property_id` WHERE `user_id`= "+str(uid)+" GROUP BY `visited_hotel_id` HAVING MAX(`visit_timestamp`)"
        result = Hotel.fireQuery(sql, True)
        return result

    def userSelectedCityFirstTime(self, uid, city):
        h = Hotel()
        h.make_connection()
        sql = "SELECT `visit_timestamp` FROM `user_history` WHERE `user_id`= "+str(uid)+" AND `visited_city` = '"+city+"'"
        result = Hotel.fireQuery(sql, True)
        print(result)
        if result is not None:
            if result==0 or len(result)<=0:
                return True
        return False



