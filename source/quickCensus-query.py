#!/usr/bin/env python3

### testing sqlite queries


# New York – Overcast ☁️   🌡️+25°F (feels +16°F, 80%) 🌬️↓6mph 🌔&m Wed Feb  1 07:15:58 2023
# W5Q1 – 32 ➡️ 332 – 266 ❇️ 98


import sqlite3
from time import time
import sys

import json

from config import INDEX_DB, log


MYINPUT = sys.argv[1]

MYITEMS = MYINPUT.split()
nParam =  len(MYITEMS)
itemCount = 0

MYINPUT_state = '' # value for US state
StateFilterString = ''
MYINPUT_state_abb = ''

MYINPUT_factor = 1 #value for percentages
PercentString = ''

MYINPUT_age = '' #value for age
AgeFilterString = ''

MYINPUT_race = '' #value for race

MYINPUT_sex = '' #value for sex

MYINPUT_latino = '' #value for latino

MYINPUT_county = '' #value for county

UStotPop = 329484123

with open('fips_states.json') as json_file:
    fips_states = json.load(json_file)

 


myOperator = ''
myOperatorString = ''


# mapping columns to add if filtering by race, sex, hispanic
myFinalMap = list(range(2, 18))
raceMapExcl = {"eur": [6,7,14,15,4,5,12,13,8,9,16,17], "amr": [2,3, 10,11,4,5,12,13,8,9,16,17],"aaa": [2,3, 10,11,6,7,14,15,8,9,16,17],"asi": [2,3, 10,11,6,7,14,15,4,5,12,13]}
sexMap = {"f": [2, 4, 6, 8, 10, 12, 14, 16], "m": [3, 5, 7, 9, 11, 13, 15, 17]} #fields to exclude for each sex
hisMap = {"h": list(range(2, 10)),"n": list(range(10, 18))}



for currItem in MYITEMS:
    
    if '+' in currItem:  # some age or above
        myOperator = '>='
        myOperatorString = '≥'
        MYINPUT_age = currItem.replace('+', '')
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    
    
    elif currItem[-1] == "-": # some age or below
        myOperator = '<='
        myOperatorString = '≤'
        MYINPUT_age = currItem.replace('-', '')
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    
    
    elif '-' in currItem: #age range
        myOperator = myOperatorString = ' between '
        MYINPUT_age = currItem.replace('-', ' AND ')
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    

    elif currItem.isdigit(): # exact age
        myOperator = myOperatorString = '='
        MYINPUT_age = currItem
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    
    
    
    if '%' in currItem: # percent
        MYINPUT_factor = currItem.replace('%', '')
        MYINPUT_factor = float(MYINPUT_factor)
        PercentString = f"({currItem})"
        #if MYINPUT_factor >= 1:
        MYINPUT_factor = MYINPUT_factor/100

    if ':' in currItem: # prevalence per 100k
        MYINPUT_factor = currItem.replace(':', '')
        MYINPUT_factor = (int(MYINPUT_factor))*0.00001
        PercentString = f"({currItem}100,000)"
        

    if currItem.isalpha(): # text item: could be state (2 char), or sex (1) or race (3), or latino (1)
        
        #state
        if len(currItem) == 2:
            itemCount += 1
            MYINPUT_state_abb = currItem
            try:
                MYINPUT_state = fips_states[currItem.upper()]['state']
            except:
                resultErr= {"items": [{
                    "title": "No matches",
                    "subtitle": "Enter a valid state abbreviation",
                    "arg": "",
                    "icon": {
                        "path": "icons/Warning.png"
                        }
                    
                }]}
                print (json.dumps(resultErr))

            
            
            StateFilterString = f'StateName LIKE "{MYINPUT_state}"'
            
        # race
        elif len (currItem) == 3 and currItem.casefold() in raceMapExcl.keys(): #race
            MYINPUT_race = currItem
            myFinalMap = [i for i in myFinalMap if i not in raceMapExcl[currItem.casefold()]]
        # sex
        elif len (currItem) == 1 and currItem.casefold() in sexMap.keys(): #male/female
            MYINPUT_sex = currItem
            myFinalMap = [i for i in myFinalMap if i not in sexMap[currItem.casefold()]]
       
        elif len (currItem) == 1 and currItem.casefold() in hisMap.keys(): #hispanic vs. not
            MYINPUT_latino = currItem
            myFinalMap = [i for i in myFinalMap if i not in hisMap[currItem.casefold()]]
            
    

def queryCensus ():
    result = {"items": [], "variables":{}}
    whereClause = ''
    myStateIcon = ''
    connString = ''
    AgeString = ''
    percentSubtitle = ''

    if MYINPUT_age:
        AgeString = f"age {myOperatorString} {MYINPUT_age}yo "


    db = sqlite3.connect(INDEX_DB)
    cursor = db.cursor()

    if itemCount:
        whereClause = " WHERE "
        if itemCount == 2:
            connString = ' AND '

        
    #MYQUERY = "%" + MYINPUT_state + "%"
    queryString = f"""SELECT *
        FROM statesPOP {whereClause} 
        {AgeFilterString}{connString}{StateFilterString}"""
    
  
    try:
        cursor.execute(queryString)
        
        rs = cursor.fetchall()

        myFinalResult = (sum(sum(i[xx] for xx in myFinalMap) for i in rs)) * MYINPUT_factor
        percentUS = (myFinalResult/UStotPop)*100
        
        
        if (MYINPUT_state or MYINPUT_age) and (MYINPUT_race or MYINPUT_sex or MYINPUT_latino): #if the records are filtered, provide also proportion
            myTot = (sum(i[-2] for i in rs)) * MYINPUT_factor
            myTot = int(myTot)
            percentFin = (myFinalResult/myTot)*100
            percentSubtitle = f"– {percentFin:.1f}% of {AgeString} {MYINPUT_state_abb.upper()}"


        

        if MYINPUT_state:
            myStateIcon = f'icons/{MYINPUT_state_abb}.png'
            myStateString = MYINPUT_state
        else: 
            myStateString = "🇺🇸"
    

    



    except sqlite3.OperationalError as err:
        result= {"items": [{
        "title": "Error: " + str(err),
        "subtitle": "Some error",
        "arg": "",
        "icon": {

                "path": "icons/Warning.png"
            }
        }]}
        print (json.dumps(result))
        raise err

    if (rs):
                
        outputString = f"{myStateString} {myFinalResult:,.0f} {PercentString} {AgeString} {MYINPUT_race.upper()} {MYINPUT_sex.upper()} {MYINPUT_latino.upper()}"
        subtitleString = f"{percentUS:.1f}% of 🇺🇸 pop {percentSubtitle}"
            
                 
        
        #### COMPILING OUTPUT    
        result["items"].append({
        "title": outputString,
        "subtitle": subtitleString,
        "arg": f"{outputString}\n{subtitleString}",
        "variables": {
        },
        
        "icon": {   
        
        "path": myStateIcon
    }
        

        })
        

                

        print (json.dumps(result))

    

    
    if MYINPUT and not rs:
        resultErr= {"items": [{
            "title": "No matches",
            "subtitle": "Try a different query",
            "arg": "",
            "icon": {
                "path": "icons/Warning.png"
                }
            
                }]}
        print (json.dumps(resultErr))



def main():
    main_start_time = time()
    queryCensus ()
    main_timeElapsed = time() - main_start_time
    log(f"\nscript duration: {round (main_timeElapsed,3)} seconds")
    
if __name__ == '__main__':
    main ()




""" notes
going through the entire 4M records: 3.4 sec (and then it takes some time to load the JSON output)
"""