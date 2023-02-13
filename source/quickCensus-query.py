#!/usr/bin/env python3

"""  **** quickCensus query ****
a script to query and make calculations on demographic data, with a function to calculate 
carriers if OR, disease, and MAF are provided. 

New York – Overcast ☁️   🌡️+25°F (feels +16°F, 80%) 🌬️↓6mph 🌔&m Wed Feb  1 07:15:58 2023
W5Q1 – 32 ➡️ 332 – 266 ❇️ 98

"""


import sqlite3
from time import time
import sys
import math
import json

from config import INDEX_DB, log, UStotPop


MYINPUT = sys.argv[1]

MYITEMS = MYINPUT.split()
MYITEMS = [*set(MYITEMS)] #eliminating exact duplicates
itemCount = 0

MYINPUT_state = '' # value for US state
StateFilterString = ''
CountryFilterString = ''
MYINPUT_state_abb = ''

MYINPUT_factor = 1 #value for percentages
PercentString = ''

MYINPUT_age = '' #value for age
AgeFilterString = ''

MYINPUT_race = '' #value for race

MYINPUT_sex = '' #value for sex

MYINPUT_latino = '' #value for latino

MYINPUT_county = '' #value for county

MYINPUT_OR = '' # value for odds ratio
ORString = ''

MYINPUT_MAF = '' #value for MAF
MAFString = ''


MYINPUT_DIS = '' #value for disease prevalence
DISString = ''

OregonFlag = False # needed to disambiguate odds ratio and Oregon (or any state entered)

# loading the fips codes for states
with open('fips_states.json') as json_file:
    fips_states = json.load(json_file)

 

def has_numbers(inputString):
# function to check if a string has both numbers and letters (for OR, MAF, DIS entries)
    hasNumbers = any(char.isdigit() for char in inputString)
    hasLetters = any(char.isalpha() for char in inputString)
    return hasNumbers and hasLetters

def predictCarriers (population, MAF, OR, DiseasePrevalence):
    pDis_A = DiseasePrevalence/(MAF+((1-MAF)/OR)) # probability of having the disease given alt allele
    pDis_a = pDis_A/OR # probability of having the disease given ref allele
    
    # cases
    pDis = int(population * DiseasePrevalence) #number of people with disease
    pDA = pDis_A * MAF
    ExpDA = round(population * pDA)
    percentDA = (ExpDA/pDis)*100
    nonZeroDA = math.ceil(abs(math.log10(percentDA)))

    # controls
    pControls = population - pDis
    ExpCont = round((population * MAF)-ExpDA)
    percentControl = (ExpCont/pControls)*100
    nonZeroC = math.ceil(abs(math.log10(percentControl)))
    

    OR_statement = (f"Assuming MAF: {MAF}, "
    f"disease prevalence: {DiseasePrevalence}, " 
    f"OR: {OR}, "
    f"and population size: {population:,}, we estimate "
    f"{ExpDA:,}/{pDis:,} ({percentDA:.{nonZeroDA}f}%) affected carriers "
    f"and {ExpCont:,}/{pControls:,} ({percentControl:.{nonZeroC}f}%) control carriers")
    
    
    return ExpDA, OR_statement



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
    
    elif 'OR' in currItem and has_numbers (currItem): # OR -checks if numbers because of Oregon :) 
        MYINPUT_OR = currItem.replace('OR', '')
        MYINPUT_OR = float(MYINPUT_OR)
        ORString = f"(OR: {MYINPUT_OR})"
        
    elif 'MAF' in currItem and has_numbers (currItem): 
        MYINPUT_MAF = currItem.replace('MAF', '')
        MYINPUT_MAF = float(MYINPUT_MAF)
        MAFString = f"(MAF: {MYINPUT_MAF})"
    
    elif 'DIS' in currItem and has_numbers (currItem): 
        MYINPUT_DIS = currItem.replace('DIS', '')
        MYINPUT_DIS = float(MYINPUT_DIS)
        DISString = f"(MAF: {MYINPUT_DIS})"
        
    
    elif '%' in currItem: # percent
        MYINPUT_factor = currItem.replace('%', '')
        MYINPUT_factor = float(MYINPUT_factor)
        PercentString = f"({currItem})"
        #if MYINPUT_factor >= 1:
        MYINPUT_factor = MYINPUT_factor/100

    elif ':' in currItem: # prevalence per 100k
        MYINPUT_factor = currItem.replace(':', '')
        MYINPUT_factor = (int(MYINPUT_factor))*0.00001
        PercentString = f"({currItem}100,000)"
        

    elif currItem.isalpha(): # text item: could be state (2 char), or sex (1) or race (3), or latino (1)
        
        #state
        if len(currItem) == 2:
            if currItem =="OR" and OregonFlag == True: # OR -checks if numbers because of Oregon :) 
                break
    
            itemCount += 1
            MYINPUT_state_abb = currItem
            
            try:
                MYINPUT_state = fips_states[currItem.upper()]['state']
                if MYINPUT_state:
                    OregonFlag = True
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
        
        else:
            CountryFilterString = f'Area LIKE "{currItem}%"'
            
    

def queryCensus ():
    result = {"items": [], "variables":{}}
    whereClause = ''
    myStateIcon = ''
    connString = ''
    AgeString = ''
    percentSubtitle = ''
    ORblock = ''
    ORstatement = ''
    
    if MYINPUT_age:
        AgeString = f"age {myOperatorString} {MYINPUT_age}yo "


    db = sqlite3.connect(INDEX_DB)
    cursor = db.cursor()

    if itemCount:
        whereClause = " WHERE "
        if itemCount == 2:
            connString = ' AND '

        
    
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
            myStateIcon = f'icons/US.png'

      

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

    if MYINPUT_OR or MYINPUT_MAF or MYINPUT_DIS:
        if MYINPUT_DIS:
            DIScheck = f"DIS: ✅"
        else:
            DIScheck = f"DIS: ❌"
        
        if MYINPUT_OR:
            ORcheck = f"OR: ✅"
        else:
            ORcheck = f"OR: ❌"
        
        if MYINPUT_MAF:
            MAFcheck = f"MAF: ✅"
        else:
            MAFcheck = f"MAF: ❌"
                
        ORblock = f"{ORcheck}-{DIScheck}-{MAFcheck}"
        if MYINPUT_OR and MYINPUT_MAF and MYINPUT_DIS:
            predictedCarriers, ORstatement = predictCarriers (
                population=myFinalResult, 
                MAF=MYINPUT_MAF, 
                OR= MYINPUT_OR,
                DiseasePrevalence=MYINPUT_DIS)
            
            ORblock = f"CALCULATING on {myFinalResult}"

    # WORLD RESULTS
    WorldQueryString = f"""SELECT Area, Total
        FROM worldPOP WHERE Area IN ('EUROPE', 'WORLD','AFRICA','ASIA','NORTHERN AMERICA','LATIN AMERICA AND THE CARIBBEAN','OCEANIA') ORDER BY Total DESC"""
    
    cursor.execute(WorldQueryString)
    rs_EU = cursor.fetchall()

    
    if (rs):
                
        outputString = f"{myStateString} {myFinalResult:,.0f} {PercentString} {AgeString} {MYINPUT_race.upper()} {MYINPUT_sex.upper()} {MYINPUT_latino.upper()}"
        subtitleString = f"{percentUS:.1f}% of 🇺🇸 pop {percentSubtitle} {ORblock}"
            
                 
        
        #### COMPILING OUTPUT    
        result["items"].append({
        "title": outputString,
        "subtitle": subtitleString,
        "arg": f"{outputString}\n{subtitleString}",
        "variables": {"ORstatement": ORstatement,
        "POPstatement": f"{outputString} ({subtitleString})"
        },
        
        "icon": {   
        
        "path": myStateIcon
    }
        

        })
        
        
        for r_EU in rs_EU:
            finalWorld = round((r_EU[1]*1000) * MYINPUT_factor)
            myStateIcon = f'icons/{r_EU[0]}.png'
            
            result["items"].append({
                    "title": f"{finalWorld:,} {PercentString}",
                    "subtitle": r_EU[0],
                    
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