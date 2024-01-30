import sqlite3
import os

con = sqlite3.connect(os.path.join('crawler', 'crawled_webpages.db'))

cur = con.cursor()

res = cur.execute("SELECT name FROM sqlite_master")
tablenames = [name[0] for name in res.fetchall()]
print(tablenames)

cur.close()
con.close()