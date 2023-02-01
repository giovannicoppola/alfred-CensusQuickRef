#!/usr/bin/env python3

### testing sqlite queries


# New York – Overcast ☁️   🌡️+25°F (feels +16°F, 80%) 🌬️↓6mph 🌔&m Wed Feb  1 07:15:58 2023
# W5Q1 – 32 ➡️ 332 – 266 ❇️ 98


import sqlite3
from time import time

from config import INDEX_DB, log


def queryCensus ():
    #result = {"items": [], "variables":{}}


    db = sqlite3.connect(INDEX_DB)
    cursor = db.cursor()

    MYINPUT= "calif"
   
    
    MYQUERY = "%" + MYINPUT + "%"
    
  
    try:
        cursor.execute("""SELECT *
        FROM statesPOP
        WHERE StateName    LIKE ?""", (MYQUERY,))
        
        rs = cursor.fetchall()
    



    except sqlite3.OperationalError as err:
        
        print ("error")
        raise err

    if (rs):
        myResLen = len (rs)
        countR=1
        
        for r in rs:
            
                 
        
            print (f"State: {r[1]}, age: {r[2]}")
            countR += 1  

                

    print (countR)

    if MYQUERY and not rs:
        print ("no results")
        



def main():
    main_start_time = time()
    queryCensus ()
    main_timeElapsed = time() - main_start_time
    print(f"\nscript duration: {round (main_timeElapsed,3)} seconds")
    
if __name__ == '__main__':
    main ()



