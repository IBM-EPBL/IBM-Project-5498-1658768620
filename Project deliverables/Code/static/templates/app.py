import numpy as np
import os
from tensorflow import keras

from keras import models
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input
import requests
from flask import Flask, request, render_template, redirect, url_for
from cloudant.client import Cloudant
model = load_model(r"diabetic-retinopathy.h5")
app = Flask(__name__)


# Authenticate using an IAM API key
client = Cloudant.iam('6093b3f5-a08d-4d7f-a67d-be6a5da5b604-bluemix', 'x8LWjxCZ9uCarheKF7suAynM32YmWvvYxlBGjuUn2eij', connect=True)
# Create a database using an initialized client
#my_database = client.create_database('my_db')

#Retrieve the existing database
my_database = client["my_database"]
print(my_database.exists())
# if my_database.exists():
#     print("Database '{0}' successfully created.".format('my_db'))


# default home page or route
@app.route('/')
def index():
    return render_template('home.html')

@ app.route('/home')
def home():
    return render_template("home.html")

# '''@ app.route('/register')
# def register():
#     return render_template("register.html")'''

# registration page
@ app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "POST":
        print("processing...")
        name =  request.form.get("name")
        mail = request.form.get("emailid")
        mobile = request.form.get("num")
        pswd = request.form.get("pass")
        data = {
            'name': name,
            'mail': mail,
            'mobile': mobile,
            'psw': pswd
        }
        print(data)
        query = {'mail': {'$eq': data['mail']}}
        docs = my_database.get_query_result(query)
        print(docs)
        print(len(docs.all()))
        if (len(docs.all()) == 0):
            url = my_database.create_document(data)
            print("Success")
            return render_template("register.html", pred=" Registration Successful , please login using your details ")
        else:
            print("Already present")
            return render_template('register.html', pred=" You are already a member , please login using your details ")
    else:
        return render_template('register.html')
    

@ app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        user = request.form.get('mail')
        passw = request.form.get('pass')
        print(user, passw)
        query = {'_id': {'$eq': user}}
        docs = my_database.get_query_result(query)
        print(docs)
        print(len(docs.all()))
        # if (len(docs.all()) == 0):
        #     print("Not found")
        #     return render_template('login.html', pred="The username is not found.")
        # else:
        #     if ((user == docs[0][0]['_id'] and passw == docs[0][0]['pswd'])):
        #         print("Success")
        return redirect(url_for('predict'))
            # else:
            #     print('Invalid User')
    else:
        return render_template('login.html')

@ app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        print("in post")
        f = request.files['image']
        print("image received")
        print(f)
        # getting the current path 1.e where app.py is present
        basepath = os.path.dirname(__file__)
        print ( " current path " , basepath )
        # from anywhere in the system we can give image but we want that
        filepath = os.path.join(basepath, 'uploads', f.filename)
        #print ( " upload folder is " , filepath )
        f.save(filepath)
        img = image.load_img(filepath, target_size=(299, 299))
        x = image.img_to_array(img)  # ing to array
        x = np.expand_dims(x, axis=0)  # used for adding one more dimension
        #print ( x )
        img_data = preprocess_input(x)
        prediction = np.argmax(model.predict(img_data), axis=1)
        # prediction = model.predict ( x ) #instead of predict_classes ( x ) we can use predict ( X ) ---- > predict_classes ( x ) gave error
        # print ( " prediction is prediction )
        index = [' No Diabetic Retinopathy ', ' Mild DR ',
                 ' Moderate DR ', ' Severe DR ', ' Proliferative DR ']
        # result = str ( index [ output [ 011 )
        result = str(index[prediction[0]])
        print(result)
        return render_template("prediction.html")
    else:
        return render_template("prediction.html")
        

@app.route('/result', methods=["GET", "POST"])
def res():
    if request.method == "POST":
        f = request.files['image']
        # getting the current path 1.e where app.py is present
        basepath = os.path.dirname(__file__)
        #print ( " current path " , basepath )
        # from anywhere in the system we can give image but we want that
        filepath = os.path.join(basepath, 'uploads', f.filename)
        #print ( " upload folder is " , filepath )
        f.save(filepath)
        img = image.load_img(filepath, target_size=(299, 299))
        x = image.img_to_array(img)  # ing to array
        x = np.expand_dims(x, axis=0)  # used for adding one more dimension
        #print ( x )
        img_data = preprocess_input(x)
        prediction = np.argmax(model.predict(img_data), axis=1)
        # prediction = model.predict ( x ) #instead of predict_classes ( x ) we can use predict ( X ) ---- > predict_classes ( x ) gave error
        # print ( " prediction is prediction )
        index = [' No Diabetic Retinopathy ', ' Mild DR ',
                 ' Moderate DR ', ' Severe DR ', ' Proliferative DR ']
        # result = str ( index [ output [ 011 )
        result = str(index[prediction[0]])
        print(result)
        return render_template('prediction.html', prediction=result)

if __name__ == "__main__":
    app.run(debug=False)