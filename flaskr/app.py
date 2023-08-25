from flask import Flask, render_template, request, redirect, url_for
from sqlite3 import connect
from qrgenerator import generateQR
from dbfunctions import *

DBDIR = r"../database/inventory.sqlite3"

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
    conn = connect(DBDIR)
    cursor = conn.cursor()
    items = cursor.execute('select * from Items').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add_items/', methods=['POST', 'GET'])
def add_items():
    return render_template('add_items.html')

@app.route('/enter_item_button/', methods=['POST', 'GET'])
def enter_item_button():
    if request.method == 'POST':
        insertItemQuery(request.form['snumber'], request.form['iname'])
        generateQR(request.form['snumber'], request.form['iname'])
        return redirect(url_for('index'), code=302)
    else:
        return redirect(url_for('add_items'), code=302)

@app.route('/item_page/<item>', methods=['POST','GET'])
def item_page(item):
    conn = connect(DBDIR)
    cursor = conn.cursor()
    fetched_data = cursor.execute('select Dates, '+'"'+item+'" from Inventory').fetchall()
    name = cursor.execute('select ItemName from Items where SerialNumber == '+'"'+item+'"').fetchall()

    data = []
    for d in fetched_data:
        data.append({'Date':d[0], 'Inventory':d[1], 'Sales':0, 'Production':0})
    
    for ind, date in enumerate(data):
            if ind < len(data) - 1:
                if data[ind+1]['Inventory'] - data[ind]['Inventory'] > 0:
                    data[ind+1]['Production'] = data[ind+1]['Inventory'] - data[ind]['Inventory']
                else:
                    data[ind+1]['Production'] = 0

            if ind < len(data) - 1:
                if data[ind]['Inventory'] - data[ind+1]['Inventory'] > 0:
                    data[ind+1]['Sales'] = data[ind]['Inventory'] - data[ind+1]['Inventory']
                else:
                    data[ind+1]['Sales'] = 0

    return render_template('item_page.html', 
                           title='Item Details', 
                           item=item, 
                           name=name[0][0], 
                           data=data)

@app.route('/edit_inv/', methods=['POST', 'GET'])
def edit_inv():
    conn = connect(DBDIR)
    cursor = conn.cursor()
    index = request.referrer.rindex('/')
    item = cursor.execute("select ItemName from Items where SerialNumber="+str(request.referrer[index+1:])).fetchall()
    actionName = 'Default Name'
    if request.args.get('actionRoute') == "add_inv":
        actionName = "New Inventory"
    elif request.args.get('actionRoute') == "add_sale":
        actionName = "New Sale"
    elif request.args.get('actionRoute') == "add_prod":
        actionName = "New Production"
    return render_template('edit_inv.html', 
                           serial= request.referrer[index:],
                           item=item[0][0],
                           actionRoute=request.args.get('actionRoute'),
                           actionName=actionName)


@app.route('/add_inv/<serial>', methods = ['POST', 'GET'])
def add_inv(serial):
    if request.method == 'POST':
        conn = connect(DBDIR)
        cursor = conn.cursor()        

        insertInventoryQuery(request.form['date'], serial, request.form['value'])

        return redirect(url_for('item_page', item=serial), code=302)

@app.route('/add_sale/<serial>', methods = ['POST', 'GET'])
def add_sale(serial):
    if request.method == 'POST':
        conn = connect(DBDIR)
        cursor = conn.cursor()        

        current_val = cursor.execute('''Select "'''+serial+'''" from Inventory''').fetchall()
        conn.close()
        new_val = float(current_val[-1][0]) - float(request.form['value'])
        insertInventoryQuery(request.form['date'], serial, new_val)

        return redirect(url_for('item_page', item=serial), code=302)

@app.route('/add_prod/<serial>', methods = ['POST', 'GET'])
def add_prod(serial):
    if request.method == 'POST':
        conn = connect(DBDIR)
        cursor = conn.cursor()
        
        current_val = cursor.execute('''Select "'''+serial+'''" from Inventory''').fetchall()
        conn.close()
        new_val = float(request.form['value']) + float(current_val[-1][0])
        insertInventoryQuery(request.form['date'], serial, new_val)

        return redirect(url_for('item_page', item=serial), code=302)

if __name__ == "__main__":
    app.directory="/DBApp"
    app.run(host='127.0.0.1', port=5000)
