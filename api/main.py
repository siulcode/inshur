import flask
from flask import jsonify, request
from mysql.connector import MySQLConnection, Error
from lib.python_mysql_dbconfig import read_db_config
from lib.catwarlord import CatWarlord


api_helper = CatWarlord()
app = flask.Flask(__name__)
app.config["DEBUG"] = True

####################################
# RUNTIME STARTS HERE

# WEB ROUTES #


@app.route('/', methods=['GET'])
def home():
    facts = api_helper.filter_warlord_facts()  # Fetch new data
    api_helper.insert_facts(facts)
    return '''
    <h1>Meaw!</h1>
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
        api_helper.delete_fact_entry(id)
        return "Fact with ID: {} has been deleted".format(id)
    else:
        return "<p>Error 405 Method Not Allowed", 405


@app.errorhandler(404)
def page_not_found(e):
    return "<p>Meou! This cat food is yucky and can't be found!</p>", 404


# START WEB SERVER #
app.run()
