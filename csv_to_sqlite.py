import sqlite3, math
from api.capacity import BoulderbarCapacity

df = BoulderbarCapacity.data_frame('./boulderbar-capacity-log.csv')

entries = []

for i, row in df.iterrows():
    entry = f"('{i}', {', '.join(['NULL' if math.isnan(v) else str(v) for v in row.values])})"
    entries.append(entry)
    #print(entry)
 
entries = ',\n'.join(entries)
#print(entries)
 
con = sqlite3.connect("boulderbar-capacity-log.db")
cur = con.cursor()
try:
    res = cur.execute(f"CREATE TABLE log(Date primary key, {', '.join(df.columns)})")
except:
    pass

res = cur.execute("SELECT name FROM sqlite_master")
#print(res.fetchone())

insert_cmd = f"""
    INSERT INTO log VALUES
        {entries}
"""

#cur.execute(insert_cmd)
#con.commit()

#res = cur.execute("SELECT * FROM log")
#for e in res.fetchall():
#    print(e)
 
res = cur.execute("SELECT * FROM log WHERE Date >= '2024-01-06' AND Date < '2024-01-09'")
for e in res.fetchall():
    print(e)
    
con.close()