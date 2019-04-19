from flask import Flask, render_template, session, request, redirect, url_for
from model import db, User, Hotel, PopularHotels, RecommendHotels, TrackActivity
from forms import *
import pickle
import logging
import traceback



app = Flask(__name__)
app.secret_key = "9d41cbf4380525bd125213f1ded6c8d61770ae17"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:h3llo2u@localhost/hotels'
db.init_app(app)

classifier_f = open("logregclassifier_stream_hacker.pickle", "rb")
classifier = pickle.load(classifier_f)
classifier_f.close()


@app.route("/")
def index():
    if 'email' in session:
        return redirect(url_for('home'))
    return render_template("index.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if 'email' in session:
        return redirect(url_for('home'))
    form = SignupForm()
    if request.method == "POST":
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            # handle form submission
            fname = form.first_name.data
            lname = form.last_name.data
            email = form.email.data
            passw = form.password.data
            user = User.query.filter_by(email=email).first()
            if user is None:
                newuser = User(fname, lname, email, passw)
                db.session.add(newuser)
                db.session.commit()
                session['email'] = newuser.email
                return redirect(url_for("home"))
    elif request.method == "GET":
        return render_template("signup.html", form=form)

@app.route("/logout")
def logout():
    if 'email' in session:
        session.pop('email', None)
    return redirect(url_for('index'))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if 'email' in session:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == "POST":
        if form.validate() == False:
            return render_template('login.html', form=form)
        else:
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                session['email'] = form.email.data
                return redirect(url_for("home", showlogin=False))
            else:
                return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template('login.html', form=form, showlogin=False)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/home", methods=['POST', 'GET'])
def home():
    if 'email' not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session['email']).first()
    username = User.query.filter_by(email=session['email']).first().firstname
    
    # check whether user history exists
    ta = TrackActivity()
    activityList = ta.getUserActivity(user.id)

    # activityList is a list containing dictionaries of records of user_history table

    # now check if the activity list has something and if it has then already show the recommendations based on visited_hotels
    recommendationsList = []
    if activityList is not None and len(activityList)>0:
        # recommendationsList is a list that contains lists and each list has a 2 dicts as 2 hotels(record) for recommendation
        for activityDict in activityList:
            rh = RecommendHotels()
            try:
                recommendations = rh.recommendUsingKNN(activityDict['visited_hotel_id'], activityDict['city'], count=2)
                recommendationsList.append(recommendations)
            except Exception as e:
                logging.error(traceback.format_exc())
            # print(recommendations)
    # print(activity)

    

    form = CityForm()
    if request.method == "POST":
        if form.validate() == False:
            return render_template("home.html",user=username, useremail=session['email'], form=form, showlogin=False)
        else:
            # handle the form submission
            city = form.city.data
            ph = PopularHotels()
            ph.make_connection()
            final_hotels = ph.getPopularHotels(city)

            #check if the user has selected the city of first time, if yes then record this as new activity
            # record activity with first hotel of popular final_hotels list
            try:
                if user.id is None or len(str(user.id))<=0:
                    return redirect(url_for("home"))
                else:
                    if ta.userSelectedCityFirstTime(user.id, city)==True:
                        # record browsing history of user
                        ta.recordActivity(user.id, str(final_hotels[0]['property_id']), str(city))
            except Exception as e:
                logging.error(traceback.format_exc())

            # print(final_hotels)
            if activityList is not None and len(activityList)>0:
                return render_template("home.html", user=username, useremail=session['email'], form=form, showlogin=False, hotels=final_hotels, recommendations=recommendationsList)
            else:
                return render_template("home.html", user=username, useremail=session['email'], form=form, showlogin=False, hotels=final_hotels)

    elif request.method == "GET":
        if activityList is not None and len(activityList)>0:
            return render_template("home.html",user=username, useremail=session['email'], form=form, showlogin=False, recommendations=recommendationsList)
        else:
            return render_template("home.html",user=username, useremail=session['email'], form=form, showlogin=False)

@app.route("/fetchmorehotels", methods=['POST', 'GET'])
def fetchmore():
    if request.method == "POST":
        # handle the form submission
        datastring= str(request.get_data())[2:-1]
        city, sep, page = datastring.partition('&')
        city = city[5:]
        page = page[5:]
        try:
            ph = PopularHotels()
            ph.make_connection()
            final_hotels = ph.getPopularHotels(city, offset=int(page)*5, count=5)
            return render_template("fetchmorehotels.html", hotels=final_hotels)
        except Exception as e:
            return render_template("fetchmorehotels.html", hotels=[])


@app.route("/submitreview", methods=['POST', 'GET'])
def submitreview():
    if request.method == "POST":
        # handle the form submission
        datastring= str(request.get_data())[2:-1]
        # print(datastring)
        hid, sep, review = datastring.partition('&')
        hid = hid[4:]
        review = review[7:]
        print(hid, review)
        try:
            hotel = Hotel()
            hotel.make_connection()
            result, reviewclass = hotel.insertReviewClassified(hid, review, classifier)
            updated_reviews = hotel.getHotelReviews(hid)
            # print(result)
            return render_template("submitreview.html", reviews=updated_reviews,reviewclass=reviewclass)
        except Exception as e:
            return render_template("submitreview.html", reviews=hotel.getHotelReviews(hid), reviewclass=reviewclass)

@app.route("/hotel")
def hotel():
    if 'email' not in session:
        return redirect(url_for("login"))

    # reading query string
    hid = request.args.get('hotelId')
    city = request.args.get('city')

    if request.method == "POST":
        if form.validate() == False:
            pass
        else:
            return render_template("home.html", hotelId=hid, showlogin=False)

    user = User.query.filter_by(email=session['email']).first()


    if hid is None or len(hid)<=0:
        return redirect(url_for("home"))
    else:
        # record browsing history of user
        ta =  TrackActivity()
        ta.recordActivity(user.id, str(hid), str(city))
        
    h = Hotel()
    h.make_connection()
    hoteldata = h.getHotelInfo(hid)
    hoteldesc = h.getHotelDesc(hid)
    hotelfacilities = h.getAvailableFacilities(hid)
    hotelreviews = h.getHotelReviews(hid) 
    # print(hotelreviews)
    if hoteldata!=0 and len(hoteldata)>0:
        try:
            rh = RecommendHotels()
            recommendations = rh.recommendUsingKNN(hid, hoteldata[0]['city'])
            return render_template("hotel.html", hotel=hoteldata[0],hotelfac=hotelfacilities,hotelDesc=hoteldesc,hotelId=hid,reviews=hotelreviews,showlogin=False, recommendationsKNN=recommendations)
        except Exception as e:
            return render_template("hotel.html", hotel=hoteldata[0],hotelfac=hotelfacilities,hotelDesc=hoteldesc,hotelId=hid,reviews=hotelreviews,showlogin=False, recommendationsKNN=[])
    return render_template("hotel.html", hotelId=hid, showlogin=False)
    
if __name__ == "__main__":
    app.run(debug=True)