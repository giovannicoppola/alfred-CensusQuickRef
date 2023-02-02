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

MYINPUT_factor = 1 #value for percentages
PercentString = ''

MYINPUT_age = '' #value for age
AgeFilterString = ''

MYINPUT_race = '' #value for race

MYINPUT_sex = '' #value for sex

MYINPUT_latino = '' #value for latino

MYINPUT_county = '' #value for county


with open('fips_states.json') as json_file:
    fips_states = json.load(json_file)

 


myOperator = ''

raceMapExcl = {"eur": [6,7,14,15,4,5,12,13,8,9,16,17], "amr": [2,3, 10,11,4,5,12,13,8,9,16,17],"aaa": [2,3, 10,11,6,7,14,15,8,9,16,17],"asi": [2,3, 10,11,6,7,14,15,4,5,12,13]}
sexMap = {"f": [2, 4, 6, 8, 10, 12, 14, 16], "m": [3, 5, 7, 9, 11, 13, 15, 17]} #fields to exclude for each sex
hisMap = {"h": list(range(2, 10)),"n": list(range(10, 18))}

myFinalMap = list(range(2, 18))
print (myFinalMap)


for currItem in MYITEMS:
    
    if '+' in currItem:  # some age or above
        myOperator = '>='
        MYINPUT_age = currItem.replace('+', '')
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    
    
    elif currItem[-1] == "-": # some age or below
        myOperator = '<='
        MYINPUT_age = currItem.replace('-', '')
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    
    
    elif '-' in currItem: #age range
        myOperator = ' between '
        MYINPUT_age = currItem.replace('-', ' AND ')
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    

    elif currItem.isdigit(): # exact age
        myOperator = '='
        MYINPUT_age = currItem
        itemCount += 1
        AgeFilterString = f'age {myOperator} {MYINPUT_age}'
    
    
    
    
    if '%' in currItem: # percent
        MYINPUT_factor = currItem.replace('%', '')
        MYINPUT_factor = int(MYINPUT_factor)
        PercentString = f"{currItem} of "
        if MYINPUT_factor > 1:
            MYINPUT_factor = MYINPUT_factor/100

    if ':' in currItem: # prevalence per 100k
        MYINPUT_factor = currItem.replace(':', '')
        MYINPUT_factor = (int(MYINPUT_factor))*0.00001
        PercentString = f"{currItem}100,000 of "
        

    if currItem.isalpha(): # text item: could be state (2 char), or sex (1) or race (3), or latino (1)
        
        #state
        if len(currItem) == 2:
            itemCount += 1
            #MYINPUT_state = currItem
            MYINPUT_state = fips_states[currItem.upper()]['state']
            #MYINPUT_state = [d for d in fips_states if d['abbr'] == currItem]
            #print (f"this is the input state: {MYINPUT_state}")
            #MYINPUT_state = MYINPUT_state[0]['state']
            
            StateFilterString = f'StateName LIKE "{MYINPUT_state}%"'
            
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
    #result = {"items": [], "variables":{}}
    whereClause = ''
    AgeString = ''
    connString = ''

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

        myTot = (sum(i[-2] for i in rs)) * MYINPUT_factor
        myTot = int(myTot)
        

        print (f"right before the query: {myFinalMap}")
        myFinalResult = (sum(sum(i[xx] for xx in myFinalMap) for i in rs)) * MYINPUT_factor
        percentFin = (myFinalResult/myTot)*100
        myFinalResult = int(myFinalResult)
        


        if MYINPUT_state:
            myState = f"in {rs[0][1]}"
        else: 
            myState = 'in the US' 
    

    



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
        myResLen = len (rs)
        countR=1
        
        for r in rs:
            
                 
        
            #### COMPILING OUTPUT    
            result["items"].append({
            "title": f"State: {r[1]}, age: {r[2]}",
            "subtitle": f"{countR}/{myResLen:,}",
            
            "variables": {
            },
            
            "icon": {   
            
            "path": ""
        }
            

            })
            countR += 1  

                

        print (json.dumps(result))

    if MYINPUT_age:
        AgeString = f" {MYINPUT_age}yo "


    # print (countR)
    print (f"{PercentString}individuals {myOperator}{AgeString}{myState}: {myTot:,}")
    #print ()
    #print (f"{myFemales:,} females ({percentFemales:.1f}%)")
    
    print (f"Final Result: {myFinalResult:,} {MYINPUT_race} {MYINPUT_sex} {MYINPUT_latino} ({percentFin:.1f}%)")

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