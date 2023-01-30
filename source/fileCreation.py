#!/usr/bin/python3 
# giovanni
# Saturday, January 28, 2023
# New York – Overcast ☁️   🌡️+33°F (feels +24°F, 69%) 🌬️↗6mph 🌓&m Sat Jan 28 09:00:37 2023
# W4Q1 – 28 ➡️ 336 – 262 ❇️ 102

import pandas as pd
import sqlite3

from config import INDEX_DB, log

# reading the 2020 file in SAS format from the CDC website
allData = pd.read_sas('/Users/giovanni/gDrive/GitHub repos/alfred-CensusQuickRef/bigFiles/pcen_v2020_y20.sas7bdat')
print(allData.head(20))
print(allData.info())
print (allData.nunique())

totTot = allData['pop'].sum()
print (f"total population: {totTot:,}")

# counting the number of counties
myCounties = allData.groupby(['ST_FIPS','CO_FIPS']).size()
# 3,143

print(myCounties.head(20))
print(myCounties.info())
print (myCounties.nunique())



by_state = allData.groupby(['age','ST_FIPS','CO_FIPS','hisp', 'RACESEX'], as_index = False)['pop'].sum()
print(by_state.head(20))
print (by_state.nunique())

pivot_table = by_state.pivot(index = ['age','ST_FIPS','CO_FIPS'], columns=['hisp', 'RACESEX'], values='pop')
print(pivot_table.head(20))

con = sqlite3.connect(INDEX_DB)
c = con.cursor()
c.execute ("DROP TABLE IF EXISTS alldata")
allData.drop(['VINTAGE', 'YEAR','MONTH'], axis=1)     

allData = allData.astype({'ST_FIPS':'string'})
allData['ST_FIPS'] = allData['ST_FIPS'].replace('6.0','California')


allData['key'] = range(1, len(allData.index)+1)

drop_statement = f"DROP TABLE IF EXISTS alldata"
allData.to_sql("alldata", con, index=False) 



c.execute ("DROP TABLE IF EXISTS state")
by_state['key'] = range(1, len(by_state.index)+1)
by_state.to_sql("state", con, index=False) 

c.execute ("DROP TABLE IF EXISTS pivot")
pivot_table['key'] = range(1, len(pivot_table.index)+1)
pivot_table.to_sql("pivot", con, index=False) 


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

"""