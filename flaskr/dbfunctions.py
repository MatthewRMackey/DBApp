from sqlite3 import connect

DBDIR = r"../database/inventory.sqlite3"

def insertItemQuery(serial, name):
    #DB connection
    conn = connect(DBDIR)
    cursor = conn.cursor()
    cursor.execute('insert into Items (SerialNumber, ItemName) values (?,?)', (serial, name))
    cursor.execute('alter table Inventory add "'+serial+'" integer')
    cursor.execute('update Inventory set "'+serial +'" = 0').fetchall()
    
    conn.commit()
    conn.close()
    

def insertInventoryQuery(date, serial, value):
    #DB connection
    conn = connect(DBDIR)
    cursor = conn.cursor()

    #Build query
    num_keys = len(cursor.execute("select * from Items").fetchall())
    items = cursor.execute("select * from Inventory").fetchall()
    headers = '(Dates, '+''.join("'"+str(n)+"', " for n in range(1,num_keys+1))[:-2]+")"
    values = '("'+date+'", '+ ', '.join([str(n) if ind != int(serial)-1 else str(value) for ind, n in enumerate(items[-1][1:])]) +")"
    query = "insert into Inventory "+headers+" values "+values
    print(query)
    cursor.execute(query)
    conn.commit()
    conn.close()

