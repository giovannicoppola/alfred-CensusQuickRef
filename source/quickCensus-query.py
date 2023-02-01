#!/usr/bin/env python3

### Main script for the quick Census workflow


#New York – Clear ☀️   🌡️+34°F (feels +31°F, 79%) 🌬️↓2mph 🌓&m Sun Jan 29 09:14:20 2023
#W4Q1 – 29 ➡️ 335 – 263 ❇️ 101


import sqlite3
import json
import sys
import os
from time import time

from config import INDEX_DB, log

def queryCensus ():
    result = {"items": [], "variables":{}}


    db = sqlite3.connect(INDEX_DB)
    cursor = db.cursor()

    MYINPUT= sys.argv[1]


    
    
    MYQUERY = "%" + MYINPUT + "%"
    
  
    try:
        cursor.execute("""SELECT *
        FROM statesPOP
        WHERE StateName    LIKE ?""", (MYQUERY,))
        
        rs = cursor.fetchall()
    



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

    if MYQUERY and not rs:
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