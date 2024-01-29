import sqlite3

def db_create_table(tablename='webpages_age', dbname='crawled_webpages.db'):
    """Create table in database"""
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    res = cur.execute("SELECT name FROM sqlite_master")
    tablenames = [name[0] for name in res.fetchall()]

    new_tablename = tablename

    if tablename in tablenames:
        ind = 1
        new_tablename = tablename + '_' + str(ind)
        while new_tablename in tablenames:
            ind += 1
            new_tablename = tablename + '_' + str(ind)
        print(f"Table {tablename} already exists in {dbname}. Writing into {new_tablename} instead...")

    cur.execute(f"CREATE TABLE {new_tablename}(url TEXT, age INTEGER)")  # Specify column names and types
    con.commit()

    cur.close()
    con.close()

    return new_tablename # in case the tablename changed


def db_add_url(url, tablename, dbname):
    """Add url to the database + increases age of urls already in the db"""
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    try:
        cur.execute(f"UPDATE {tablename} SET age = age + 1;")
        con.commit()

        # Specify column names and types in the INSERT query
        query = f"INSERT INTO {tablename} (url, age) VALUES (?, ?);"
        con.execute(query, (url, 0))
        con.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        con.close()

# Create the table
table_name = db_create_table()

# Add URLs to the table
db_add_url("https://youtube.com/", table_name, 'crawled_webpages.db')
db_add_url("https://youtube.com/about", table_name, 'crawled_webpages.db')
