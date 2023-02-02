#!/usr/bin/env python3

### testing sqlite queries


# New York – Overcast ☁️   🌡️+25°F (feels +16°F, 80%) 🌬️↓6mph 🌔&m Wed Feb  1 07:15:58 2023
# W5Q1 – 32 ➡️ 332 – 266 ❇️ 98


import sqlite3
from time import time
import sys

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

connString = ''
myOperator = ''

raceMap = {"EUR": [2,3, 10,11],"AMR": [6,7,14,15],"AAA": [4,5,12,13], "ASI": [8,9,16,17]}
sexMap = {"Male": [2, 4, 6, 8, 10, 12, 14, 16], "Female": [3, 5, 7, 9, 11, 13, 15, 17]}
for currItem in MYITEMS:
    
    if '+' in currItem:  # some age or above
        myOperator = '>='
        MYINPUT_age = currItem.replace('+', '')
        itemCount += 1
        if itemCount > 1:
            connString = " AND "
        AgeFilterString = f'{connString}age {myOperator} {MYINPUT_age}'
    
    
    elif currItem[-1] == "-": # some age or below
        myOperator = '<='
        MYINPUT_age = currItem.replace('-', '')
        itemCount += 1
        if itemCount > 1:
            connString = " AND "
        AgeFilterString = f'{connString}age {myOperator} {MYINPUT_age}'
    
    
    elif '-' in currItem:
        myOperator = ' between '
        MYINPUT_age = currItem.replace('-', ' AND ')
        itemCount += 1
        if itemCount > 1:
            connString = " AND "
        AgeFilterString = f'{connString}age {myOperator} {MYINPUT_age}'
    

    elif currItem.isdigit(): # exact age
        myOperator = '='
        MYINPUT_age = currItem
        itemCount += 1
        if itemCount > 1:
            connString = " AND "
        AgeFilterString = f'{connString}age {myOperator} {MYINPUT_age}'
    
    


    
    print (f"item {itemCount}: {currItem}")
    
    if '%' in currItem:
        MYINPUT_factor = currItem.replace('%', '')
        MYINPUT_factor = int(MYINPUT_factor)
        PercentString = f"{currItem} of "
        if MYINPUT_factor > 1:
            MYINPUT_factor = MYINPUT_factor/100

    if currItem.isalpha(): # text item: could be state (2 char), or sex (1) or race (3), or latino (1)
        
        #state
        if len(currItem) == 2:
            # if currItem in ['EUR','AA']
            itemCount += 1
            MYINPUT_state = currItem
            if itemCount > 1:
                connString = " AND "
            
            StateFilterString = f'{connString}StateName LIKE "{MYINPUT_state}%"'
            
        # race
        elif len (currItem) == 3:
            MYINPUT_race = currItem
        # sex
        elif len (currItem) == 1:
            MYINPUT_sex = currItem


def queryCensus ():
    #result = {"items": [], "variables":{}}
    whereClause = ''
    AgeString = ''

    db = sqlite3.connect(INDEX_DB)
    cursor = db.cursor()

    if itemCount:
        whereClause = " WHERE "
        
    #MYQUERY = "%" + MYINPUT_state + "%"
    queryString = f"""SELECT *
        FROM statesPOP {whereClause}
        {AgeFilterString} {StateFilterString}"""
    
    print (queryString)
    try:
        cursor.execute(queryString)
        
        rs = cursor.fetchall()


        myTot = (sum(i[-2] for i in rs)) * MYINPUT_factor
        myTot = int(myTot)
        
        
        myMales = (sum(sum(i[xx] for xx in sexMap['Male']) for i in rs)) * MYINPUT_factor
        percentMales = (myMales/myTot)*100
        myMales = int(myMales)
        
        
        myFemales = (sum(sum(i[xx] for xx in sexMap['Female']) for i in rs)) * MYINPUT_factor
        percentFemales = (myFemales/myTot)*100
        myFemales = int(myFemales)
        

        myEUR = (sum(sum(i[xx] for xx in raceMap['EUR']) for i in rs)) * MYINPUT_factor
        percentEUR = (myEUR/myTot)*100
        myEUR = int(myEUR)
        


        if MYINPUT_state:
            myState = f"in {rs[0][1]}"
        else: 
            myState = 'in the US' 
    


        
    except sqlite3.OperationalError as err:
        
        print ("error")
        raise err

    # if (rs):
    #     myResLen = len (rs)
    #     countR=1
        
    #     for r in rs:
            
                 
        
    #         print (f"State: {r[1]}, age: {r[0]}, total: {myTot}")
    #         countR += 1  

    if MYINPUT_age:
        AgeString = f" {MYINPUT_age}yo "


    # print (countR)
    print (f"{PercentString}individuals {myOperator}{AgeString}{myState}: {myTot:,}")
    print (f"{myMales:,} males ({percentMales:.1f}%)")
    print (f"{myFemales:,} females ({percentFemales:.1f}%)")
    
    print (f"{myEUR:,} EUR ({percentEUR:.1f}%)")
    if MYINPUT and not rs:
        print ("no results")
        



def main():
    main_start_time = time()
    queryCensus ()
    main_timeElapsed = time() - main_start_time
    print(f"\nscript duration: {round (main_timeElapsed,3)} seconds")
    
if __name__ == '__main__':
    main ()



