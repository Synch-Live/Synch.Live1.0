import sqlite3
import pandas as pd
import numpy as np

# create sqlite database
con = sqlite3.connect('database.db')
""" 
# make pandas df from numpy array
data = np.array([(1, 2, 3), (4, 5, 6), (7, 8, 9)], dtype=[("a", "i4"), ("b", "i4"), ("c", "i4")])

df = pd.DataFrame(data, columns=['c', 'a'])

print(df)

# write pandas df to database
df.to_sql("test_data", con, if_exists="replace") 
"""

# read data from database into new dataframe
df_new = pd.read_sql_query("SELECT * from test_data", con)

print(df_new)

# close database connection
con.close()