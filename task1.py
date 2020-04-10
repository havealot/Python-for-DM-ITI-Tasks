import pandas as pd
import re


def clean_string(string):
    only_chars = re.sub(r"[0-9]*", "", string)
    clean_str = re.sub(r"\(.*\)", "", only_chars)
    return clean_str.strip()

# Energy Dataframe
energy = pd.read_excel('data/Energy Indicators.xls',  skiprows = range(1, 18), usecols="C:F", skipfooter=38, na_values=["..."])
energy.columns = ["Country","Energy Supply","Energy Supply per Capita","% Renewable"]
energy["Energy Supply"] = energy["Energy Supply"]*1000000
energy["Country"] = energy["Country"].apply(clean_string)
energy["Country"].replace({"Republic of Korea": "South Korea", "United States of America": "United States",
                           "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
                           "China, Hong Kong Special Administrative Region": "Hong Kong"}, inplace=True)
						   
						   
# GDP Dataframe
GDP = pd.read_csv("data/world_bank.csv", skiprows = range(4), usecols=["Country Name","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015"])
GDP.rename(columns={"Country Name": "Country"}, inplace=True)
GDP["Country"].replace({"Korea, Rep.": "South Korea", 
                             "Iran, Islamic Rep.": "Iran",
                             "Hong Kong SAR, China": "Hong Kong"}, inplace=True)
							 
# ScimEn Dataframe
ScimEn = pd.read_excel("data/scimagojr-3.xlsx")

# Merging the three dataframes
stp1 = ScimEn.merge(energy, on="Country")
dataset = stp1.merge(GDP, on="Country")
dataset.set_index("Country", inplace=True)

top15 = dataset.iloc[:15]

# lost entries
print("lost entries")
print(len(dataset) - len(top15))

# Pivoting the dataframe
top15_pivot = pd.pivot_table(top15, values=["2006","2007","2008","2009","2010","2011","2012","2013","2014","2015"], columns='Country')
avgGDP = top15_pivot.mean(axis=0, skipna=True).sort_values(ascending=False)
# mean value for the last 10 years for each country
print("mean value for the last 10 years for each country")
print(avgGDP)

# mean energy supply per capita
print("mean energy supply per capita")
print(top15["Energy Supply per Capita"].mean(skipna=True))

# What country has the maximum % Renewable and what is the percentage?
print("What country has the maximum % Renewable and what is the percentage")
country = top15["% Renewable"].idxmax()
val = top15["% Renewable"].max()
print((country, val))

# creating new column for citation-ratio
top15["Citation-Ratio"] = top15["Self-citations"]/top15["Citations"]
country = top15["Citation-Ratio"].idxmax()
val = top15["Citation-Ratio"].max()
# What is the maximum value for this new column, and what country has the highest ratio?
print("What is the maximum value for this new column, and what country has the highest ratio?")
print((country, val))

# Create a new column with a 1 if the country's % Renewable value is at or above the median for all countries in the top 15, 
# and a 0 if the country's % Renewable value is below the median.
mean = top15["% Renewable"].mean()
top15["HighRenew"] = [1 if p > mean else 0 for p in top15['% Renewable']]

# Creating new column for population estimation
top15["Population"] = top15["Energy Supply"] / top15["Energy Supply per Capita"]


ContinentDict  = {'China':'Asia', 
                  'United States':'North America', 
                  'Japan':'Asia', 
                  'United Kingdom':'Europe', 
                  'Russian Federation':'Europe', 
                  'Canada':'North America', 
                  'Germany':'Europe', 
                  'India':'Asia',
                  'France':'Europe', 
                  'South Korea':'Asia', 
                  'Italy':'Europe', 
                  'Spain':'Europe', 
                  'Iran':'Asia',
                  'Australia':'Australia', 
                  'Brazil':'South America'}

#top15.set_index("Country", inplace=True)
#top15.reset_index(inplace=True)

# map continent dictionary to the index column to create continent column
top15["Continent"] = top15.index.map(ContinentDict)

# make new aggregated dataframe
aggregatedDataframe = top15.groupby('Continent').agg({"Rank": ["count"],'Population' :['sum', 'mean', 'std' ]})

# return a DataFrame with index named Continent ['Asia', 'Australia', 'Europe', 'North America', 'South America'] and columns ['size', 'sum', 'mean', 'std']
print("Aggregated dataframe.. 'size', 'sum', 'mean', 'std'")
print(aggregatedDataframe.head())
