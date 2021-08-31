import flask
import requests
import string
from flask import jsonify, request
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import datetime, timedelta

app = flask.Flask(__name__)
beamed_api = 'http://158.247.202.14:4141/facts'
config_path = "~/inshur/api/"
app.config["DEBUG"] = True


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def fetch_feline_facts():
    resp = requests.get(beamed_api)
    if resp.status_code == 200:
        return resp.json()


def filter_warlord_facts():
    fact_list = []
    name_prefix = []
    data = fetch_feline_facts()
    alphabet = string.ascii_uppercase
    for index, letter in enumerate(alphabet):
        if index % 2 == 0:
            name_prefix.append(letter)
    for item in data:
        str_dob = item.get('date_of_birth')
        first_name = item.get('first_name')
        obj_dob = datetime.strptime(str_dob, '%Y-%m-%d')
        allowed_dob = datetime.now() - timedelta(days=3650)
        if allowed_dob < obj_dob and first_name[0] in name_prefix:
            fact_list.append(item)
    if fact_list is not None:
        return fact_list
    else:
        raise ValueError('Nothing found based specified criteria')


def insert_facts(facts):
    query = '''
    INSERT INTO catwarrior_facts(
            cuid,date_of_birth,fact,first_name,last_name
        )
    VALUES(%s,%s,%s,%s,%s)'''
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        for item in facts:
            cuid = item.get('cuid')
            date_of_birth = item.get('date_of_birth')
            fact = item.get('fact')
            first_name = item.get('first_name')
            last_name = item.get('last_name')
            args = (cuid, date_of_birth, fact, first_name, last_name)
            cursor = conn.cursor()
            cursor.execute(query, args)
            if cursor.lastrowid:
                print('last insert id', cursor.lastrowid)
            else:
                print('last insert id not found')
            conn.commit()
    except Error as e:
        print('Error:', e)
    finally:
        cursor.close()
        conn.close()


def delete_fact_entry(id):
    db_config = read_db_config()
    query = "DELETE FROM catwarrior_facts WHERE id = %s"
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, (id,))
        conn.commit()
    except Error as error:
        print(error)
    finally:
        cursor.close()
        conn.close()


@app.route('/', methods=['GET'])
def home():
    facts = filter_warlord_facts()  # Fetch new data
    insert_facts(facts)
    return '''<h1>Meaw!</h1>
<p>Endpoint to query our nifty Cat warlord API.</p>
<p>
    View all of our filtered entries here:
    <a href="https://05d2-173-63-132-127.ngrok.io/api/v1/quotes/allfacts" />
        Here
    </a>
</p>
'''


@app.route('/api/v1/quotes/allfacts', methods=['GET'])
def quote_allfacts():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM catwarrior_facts")
        rows = cursor.fetchall()
        print('Total Row(s):', cursor.rowcount)
        for row in rows:
            print(row)
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return jsonify(rows)


@app.route('/api/v1/delete/<id>', methods=['DELETE'])
def delete_fact_by_id(id):
    if request.method == 'DELETE':
        delete_fact_entry(id)
        return "Fact with ID: {} has been deleted".format(id)
    else:
        return "<p>Error 405 Method Not Allowed", 405


@app.errorhandler(404)
def page_not_found(e):
    return "<p>Meou! This cat food is yucky and can't be found!</p>", 404


app.run()
