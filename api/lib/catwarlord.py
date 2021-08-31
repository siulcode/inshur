import requests
import string
from datetime import datetime, timedelta
from mysql.connector import MySQLConnection, Error
from lib.python_mysql_dbconfig import read_db_config


class CatWarlord:

    def __init__(self):
        self.beamed_api = 'http://158.247.202.14:4141/facts'

    def fetch_feline_facts(self):
        resp = requests.get(self.beamed_api)
        if resp.status_code == 200:
            return resp.json()

    def filter_warlord_facts(self):
        fact_list = []
        name_prefix = []
        data = self.fetch_feline_facts()
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

    def insert_facts(self, facts):
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

    def delete_fact_entry(self, id):
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
