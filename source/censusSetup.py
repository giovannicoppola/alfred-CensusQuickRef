#!/usr/bin/python3 
# giovanni
# Saturday, January 28, 2023
# New York – Overcast ☁️   🌡️+33°F (feels +24°F, 69%) 🌬️↗6mph 🌓&m Sat Jan 28 09:00:37 2023
# W4Q1 – 28 ➡️ 336 – 262 ❇️ 102

"""
censusSetup
a script to create the sqlite database to be queried for the census workflow

THe source file is a script from the CDC website (Bridged-Race Population Estimates) Downloaded the SAS version. 
https://www.cdc.gov/nchs/nvss/bridged_race/data_documentation.htm#vintage2020
containing records for all US counties divided by sex, race, latino
Initial file has 4,324,768 entries, total population: 329,484,123


WOrld files downloaded here:
https://population.un.org/wpp/Download/Standard/Population/

WPP2022_POP_F01_1_POPULATION_SINGLE_AGE_BOTH_SEXES.xlsx (first tab saved as CSV, first 16 rows skipped)
WPP2022_POP_F01_2_POPULATION_SINGLE_AGE_MALE.xlsx

"""
import datetime
from time import time
import pandas as pd
import sqlite3
import os

from config import INDEX_DB, log, logF, DATA_FILE_US, DATA_FILE_WORLD



# initializing the log file    
timeStr = datetime.datetime.now().strftime ("%Y-%m-%d-%H-%M")
timeSta = datetime.datetime.now().strftime ("%Y-%m-%d at %H:%M")
myTimeStamp = f"Script run on {timeSta}"
LOG_FILE = f"../logs/{timeStr}_log.md"
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)


# function (from chatGPT) to generate one-number FIPS codes
def join_numbers(A, B):
    result = []
    for i in range(len(A)):
        a = str(A[i])
        b = str(B[i]).zfill(3)
        result.append(a + b)
    return result

def UScensus(dataFile):
    
    logF (f"# US Census catalog build\n{myTimeStamp}", file_name =  LOG_FILE)
    logF (f"\n- source file used: {dataFile}\n", file_name =  LOG_FILE)

    # reading the 2020 file in SAS format from the CDC website
    print (f"reading the SAS object in...")
    allData = pd.read_sas(dataFile)
    

    totTot = int(allData['pop'].sum())
    lenDF = len(allData.index)
    print (f"number of rows: {lenDF:,}")
    print (f"total population: {totTot:,}")

    logF (f"- number of rows: {lenDF:,}\n", file_name =  LOG_FILE)
    logF (f"- total population: {totTot:,}\n", file_name =  LOG_FILE)
    

    # counting the number of counties
    #myCounties = allData.groupby(['ST_FIPS','CO_FIPS']).size()
    # 3,143

    # reading in the FIPS codes for US states and counties
    fips = pd.read_csv ('fips_states.csv')
    fips_counties = pd.read_csv ('fips_counties.csv')
    
    # dropping columns with a single value
    allData.drop(['VINTAGE', 'YEAR','MONTH'], axis=1)     

    # turning FIPS codes to integer, then generating a unique FIPS number
    print (f"generating unique FIPS codes...")
    allData = allData.astype({'ST_FIPS':'int64'})
    allData = allData.astype({'CO_FIPS':'int64'})
    allData['fullFIPS']= join_numbers(allData['ST_FIPS'],allData['CO_FIPS'])
    allData = allData.astype({'fullFIPS':'int64'})
    
    # changing the age column from float64 to int64
    allData = allData.astype({'age':'int64'})
    

    # mapping numerical FIPS codes to strings
    print (f"mapping numerical FIPS codes to strings...")
    allData['StateName'] = allData['ST_FIPS'].map(fips.set_index('fips')['state'])
    allData['CountyName'] = allData['fullFIPS'].map(fips_counties.set_index('fips')['county_name'])

    # generating a table with all counties
    print (f"generating a table with all counties...")
    con = sqlite3.connect(INDEX_DB)
    c = con.cursor()
    

    countiesPOP = allData.pivot(index = ['age','StateName','CountyName','fullFIPS'], columns=['hisp', 'RACESEX'], values='pop')
    c.execute ("DROP TABLE IF EXISTS countiesPOP")
    
    
    ### MIGHT WANT TO RENAME COLUMNS HERE
    
    # generating a pop total for each county/age
    countiesPOP['TotalPOP']= countiesPOP.sum(axis=1)
    countiesPOP['key'] = range(1, len(countiesPOP.index)+1)
    
    
    # changing columns from float64 to int64
    for column in countiesPOP.columns:
        if countiesPOP[column].dtype == 'float64':
            countiesPOP[column] = countiesPOP[column].astype('int64')
            
    countiesPOP.to_sql("countiesPOP", con) 

    
    # generating a table with all states
    print (f"generating a table with all states...")
    by_state = allData.groupby(['age','StateName','hisp', 'RACESEX'], as_index = False)['pop'].sum()
    statesPOP = by_state.pivot(index = ['age','StateName'], columns=['hisp', 'RACESEX'], values='pop')
    c.execute ("DROP TABLE IF EXISTS statesPOP")
    
        
    # generating a pop total for each state/age
    statesPOP['TotalPOP']= statesPOP.sum(axis=1)
    statesPOP['key'] = range(1, len(statesPOP.index)+1)
    # changing columns from float64 to int64
    for column in statesPOP.columns:
        if statesPOP[column].dtype == 'float64':
            statesPOP[column] = statesPOP[column].astype('int64')
    

    statesPOP.to_sql("statesPOP", con) 


def WorldCensus (DataFileTot,DataFileM):
    """
    file info: 
    20,520 rows
    285 after removing spurious and keeping one year only
    in the Type column:
        1 World
        6 regions (africa, asia etc)
        6 income groups (high-income, middle-income etc)
        5 development groups (least developed, less developed)
        8 SDG regions (Latin America, Europe and north america) [sustainable development goals]
        2 special other (landlocked developing and small island developing)
        21 Subregions (Eastern Africa, Western Europe etc)
        236 Countries/areas
    """
    
    df = pd.read_csv(DataFileTot)
    
    df.drop(df[df['Type'] == "Label/Separator"].index, inplace = True) #removing 'separator' row
    df.drop(df[df['Year'] != 2021].index, inplace = True)  #removing anything not in 2021
    
    for column in df.columns[11:112]:
        df[column] = df[column].str.replace(' ', '').astype("Int64")
    
    df['Total'] = df[df.columns[11:112]].sum(axis=1).astype("Int64") #adding row total 

    df['Year'] = df['Year'].astype('Int64')
    df.drop(['Variant'], axis=1,inplace=True) 
    
    
    # generating a table with all world countries
    print (f"generating a table with all world countries...")
    con = sqlite3.connect(INDEX_DB)
    c = con.cursor()
    
    df.rename(columns={'Index': 'IndexCol'}, inplace=True)
    df.rename(columns={'Region, subregion, country or area *': 'Area'}, inplace=True)
    df.drop(['Notes'], axis=1,inplace=True) 
    df.drop(['SDMX code**'], axis=1,inplace=True) 
    
    print (df.info(verbose=True))
    print (df.head(10))
    
    c.execute ("DROP TABLE IF EXISTS worldPOP")
    df.to_sql("worldPOP", con) 


    
def main(args=None):
    main_start_time = time()
    #UScensus(DATA_FILE_US)
    WorldCensus (DATA_FILE_WORLD,DATA_FILE_WORLD)
    
    main_timeElapsed = time() - main_start_time
    print(f"\nTotal script duration: {round (main_timeElapsed,2)} seconds")
    logF(f"\nTotal script duration: {round (main_timeElapsed,2)} seconds", file_name =  LOG_FILE)



if __name__ == '__main__':
    main ()


""" file info
total population: 329,484,123
     age  hisp  RACESEX  VINTAGE  race4    pop    YEAR  MONTH  ST_FIPS  CO_FIPS
0    0.0   1.0      1.0   2020.0    1.0  211.0  2020.0    7.0      1.0      1.0
1    1.0   1.0      1.0   2020.0    1.0  230.0  2020.0    7.0      1.0      1.0
2    2.0   1.0      1.0   2020.0    1.0  256.0  2020.0    7.0      1.0      1.0
3    3.0   1.0      1.0   2020.0    1.0  249.0  2020.0    7.0      1.0      1.0
4    4.0   1.0      1.0   2020.0    1.0  270.0  2020.0    7.0      1.0      1.0
5    5.0   1.0      1.0   2020.0    1.0  242.0  2020.0    7.0      1.0      1.0
6    6.0   1.0      1.0   2020.0    1.0  260.0  2020.0    7.0      1.0      1.0
7    7.0   1.0      1.0   2020.0    1.0  235.0  2020.0    7.0      1.0      1.0
8    8.0   1.0      1.0   2020.0    1.0  254.0  2020.0    7.0      1.0      1.0
9    9.0   1.0      1.0   2020.0    1.0  252.0  2020.0    7.0      1.0      1.0
10  10.0   1.0      1.0   2020.0    1.0  259.0  2020.0    7.0      1.0      1.0
11  11.0   1.0      1.0   2020.0    1.0  271.0  2020.0    7.0      1.0      1.0
12  12.0   1.0      1.0   2020.0    1.0  292.0  2020.0    7.0      1.0      1.0
13  13.0   1.0      1.0   2020.0    1.0  279.0  2020.0    7.0      1.0      1.0
14  14.0   1.0      1.0   2020.0    1.0  259.0  2020.0    7.0      1.0      1.0
15  15.0   1.0      1.0   2020.0    1.0  278.0  2020.0    7.0      1.0      1.0
16  16.0   1.0      1.0   2020.0    1.0  263.0  2020.0    7.0      1.0      1.0
17  17.0   1.0      1.0   2020.0    1.0  283.0  2020.0    7.0      1.0      1.0
18  18.0   1.0      1.0   2020.0    1.0  239.0  2020.0    7.0      1.0      1.0
19  19.0   1.0      1.0   2020.0    1.0  200.0  2020.0    7.0      1.0      1.0
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 4,324,768 entries, 0 to 4324767



<class 'pandas.core.frame.DataFrame'>
RangeIndex: 4324768 entries, 0 to 4324767
Data columns (total 10 columns):
 #   Column   Dtype  
---  ------   -----  
 0   age      float64
 1   hisp     float64
 2   RACESEX  float64
 3   VINTAGE  float64
 4   race4    float64
 5   pop      float64
 6   YEAR     float64
 7   MONTH    float64
 8   ST_FIPS  float64
 9   CO_FIPS  float64
dtypes: float64(10)
memory usage: 330.0 MB
None
age          86
hisp          2
RACESEX       8
VINTAGE       1
race4         4
pop        8830
YEAR          1
MONTH         1
ST_FIPS      51
CO_FIPS     325
dtype: int64


in the final database:
Males are fields (add 1 to the fields in the documentation) 
2, 4, 6, 8, 10, 12, 14, 16







"""