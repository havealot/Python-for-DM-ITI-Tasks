import sqlalchemy as db
import pandas as pd
import numpy as np
import json
from keras.models import model_from_json



# create connection with the database
con = db.create_engine('postgresql://postgres:root@localhost/ammardb')

#First run only to load table the unscored table..
#df = pd.read_csv("pima-indians-diabetes.data.csv")
#df.to_sql('diabetes_unscored', con, if_exists='append', index=False)

# Select query that retreive only unscored data
query = """
select "Pregnancies",
"Glucose",
"BloodPressure",
"SkinThickness",
"Insulin",
"BMI",
"DiabetesPedigreeFunction",
"Age" 
from "diabetes_unscored"
except
select "Pregnancies",
"Glucose",
"BloodPressure",
"SkinThickness",
"Insulin",
"BMI",
"DiabetesPedigreeFunction",
"Age" 
from "diabetes_scored";
"""
# Load the table 
diabetes = pd.read_sql(query, con)

# open the json file for read
json_file = open('model.json', 'r')
model_json = json_file.read()
json_file.close()

# loading the model from the json file
model = model_from_json(model_json)

# loading weights to the model from h5 file
model.load_weights("model.h5")

# transforming the diabetes dataframe to numpy array to pass it to the predict function
diabetes_arr = diabetes.to_numpy()
prediction = model.predict(diabetes_arr)

# transforming the outcome to 0 or 1
scores=[]
for i in prediction:
    if i >= 0.5:
        scores.append(1)
    else:
        scores.append(0)

# add new column for Outcome 'Score' to the dataframe
diabetes['Outcome']= scores

# Insert new scored data to the diabetes_scored table
diabetes.to_sql(name = 'diabetes_scored', con=con, index = False, if_exists='append')

# crontab -e
# 0 * * * * /usr/bin/python /home/ammar/Desktop/task3/task3.py
