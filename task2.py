# Import subprocess
import time
start_time = time.time()

from subprocess import PIPE, Popen
from os import listdir
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("path", help = "Enter the desired path")
parser.add_argument("-u", "--unx", action="store_true", dest="unix_format", default=False, help="Keeps the original unix time format")
args = parser.parse_args()

checksums = {}
duplicates = []

files = [item for item in listdir(args.path) if (".json" in item)]

# Iterate over the list of files filenames
for filename in files:
    # Use Popen to call the md5sum utility
    with Popen(["md5sum", args.path+"/"+filename], stdout=PIPE) as proc:
        checksum = proc.stdout.read().split()[0]
        
        # Append duplicate to a list if the checksum is found
        if checksum in checksums:
            duplicates.append(filename)
        checksums[checksum] = filename


l = len(duplicates)
if l > 0:
    #print("Found " + str(l) + " duplicate files.")
    print("------- Duplicate Files -------")
    for i in duplicates:
        print(">  "+i)
    print("-"*31)

import json
import datetime
import pandas as pd
import re
import numpy as np


def get_browser(s):
    browser = re.search("\w*/\d\.\d", str(s))
    if browser:
        return browser.group(0)
    else:
        return None
    
def get_os(s):
    os = re.search("\([a-zA-Z0-9 \.]*", str(s))
    if os:
        return os.group(0).replace("(", "").replace(";", "")
    else:
        return None
    
def get_short(s):
    short = re.search("(http://)(www\.)?[a-zA-Z0-9]*\.[^/]*", str(s))
    if short:
        return short.group(0).replace("http://","")
    else:
        return None
    
def get_long(s):
    if type(s) is list:
        return s[0]
    else:
        return None

def get_lat(s):
    if type(s) is list:
        return s[1]
    else:
        return None

def to_human_date(d):
    if not np.isnan(d):
        return datetime.datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None
print("---------- New Files ----------")
for f in checksums.values():


    records = [json.loads(line) for line in open(args.path+"/"+f)]

    df = pd.DataFrame.from_records(records, columns=["a", "tz", "r", "u", "t", "hc", "cy", "ll"])

    df.columns = ["browser/os", "timezone", "from_url", "to_url", "time_in", "time_out", "city", "long/lat"]

    if not args.unix_format:
        df["time_in"] = df["time_in"].apply(to_human_date)
        df["time_out"] = df["time_out"].apply(to_human_date)
	    
    df["web_browser"] = df["browser/os"].apply(get_browser)
    df["operating_sys"] = df["browser/os"].apply(get_os)
    del df["browser/os"]

    df["from_url"] = df["from_url"].apply(get_short)
    df["to_url"] = df["to_url"].apply(get_short)


    df["longitude"] = df["long/lat"].apply(get_long)
    df["latitude"] = df["long/lat"].apply(get_lat)
    del df["long/lat"]

    df.dropna(inplace=True)

    df.head(5)
    new_f = args.path+"/"+f.replace("json", "csv")
    df.to_csv(new_f, index=False)
    print("New file path: "+ args.path+"/"+f.replace("json", "csv") + ", records transformed: " + str(len(df)))
print("-"*31)
print("--- Finished under "+ str(round((time.time() - start_time)*1000, 2)) +" Milliseconds. ---")