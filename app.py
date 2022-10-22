from unicodedata import name
from flask import request, Flask, render_template, redirect, session
import mysql.connector
import pandas as pd 
import numpy as np
import pickle
import os

app = Flask(__name__) 
app.secret_key=os.urandom(24)

conn=mysql.connector.connect(host="localhost",user="root",password="",database="bike")
cursor=conn.cursor()

model1 = pickle.load(open('Random.pkl', 'rb'))

def drop(test_df):
  test_df.drop([""],axis=1,inplace=True)
  return test_df

def handle_categorical(test_df):
  Brand_val= 'Brand' + '_' + test_df['Brand'][0]
  if Brand_val in test_df.columns:
    test_df[Brand_val] = 1

  Transmission_val= 'Transmission' + '_' + test_df['Transmission'][0]
  if Transmission_val in test_df.columns:
    test_df[Transmission_val] = 1
  
  return test_df

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    if 'id' in session:
      return render_template('index.html')
    else:
      return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    name=request.form.get('name')
    password=request.form.get('password')

    cursor.execute("""SELECT * FROM `user` WHERE `name` LIKE '{}' AND `password` LIKE '{}'"""
    .format(name,password))
    users=cursor.fetchall()

    if len(users)>0:
      session['id']=users[0][0]
      return redirect('/home')
    else:
      return render_template("login.html")

@app.route('/register', methods=['POST'])
def register():
    name=request.form.get('uname')
    email=request.form.get('uemail')
    password=request.form.get('password')

    cursor.execute("""INSERT INTO `user` (`id`,`name`,`email`,`password`) VALUES(NULL,'{}','{}','{}')""".format(name,email,password))
    conn.commit()

    cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""".format(email))
    myuser=cursor.fetchall()
    session['id']=myuser[0][0]
    return redirect('/home')

@app.route('/predict',methods=['POST'])
def predict():
    print('Applied Machine Learning Course')
    features = request.form
    print(features)
    Brand = features['Brand']
    Year = features['Year']
    Transmission = features['Transmission']
    Capacity = features['Capacity']
    Mileage = features['Mileage']
    Fuel_Price = features['Fuel_Price']
    USD_Rate = features['USD_Rate']
    Crude_Oil_Price = features['Crude_Oil_Price']
    
    user_input = {'Brand':[Brand],'Year':[Year],'Transmission':[Transmission],'Capacity':[Capacity],'Mileage':[Mileage], 'Fuel_Price':[Fuel_Price], 'USD_Rate':[USD_Rate],'Crude_Oil_Price':[Crude_Oil_Price]}
    test_df = pd.DataFrame(user_input)

    test_df = pd.concat([test_df],axis=1) 
             
    test_df = handle_categorical(test_df)  

    print(test_df)

    prediction = model1.predict(test_df)

    output = float(np.round(prediction[0], 2))

    print(output)

    return render_template('index.html', prediction_text='Predicted price of Bike is Rs. {}'.format(output))


if __name__ == "__main__":
    app.run(debug=True)