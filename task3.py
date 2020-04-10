import sqlalchemy as db
import pandas as pd
import numpy as np
import json
from keras.models import model_from_json



# create connection with the database
con = db.create_engine('postgresql://postgres:root@localhost/ammardb')
# Find out the tables in this DB
con.table_names()

#First run only to load table..
#df = pd.read_csv("pima-indians-diabetes.data.csv")
#df.to_sql('diabetes_unscored', con, if_exists='append', index=False)

# Create a SQL query to load the entire diabetes table
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
# View the head

json_file = open('model.json', 'r')
model_json = json_file.read()
json_file.close()

model = model_from_json(model_json)
model.load_weights("model.h5")

diabetes_arr = diabetes.to_numpy()
prediction = model.predict(diabetes_arr)

scores=[]
for i in prediction:
    if i >= 0.5:
        scores.append(1)
    else:
        scores.append(0)

diabetes['Outcome']= scores

diabetes.to_sql(name = 'diabetes_scored', con=con, index = False, if_exists='append')