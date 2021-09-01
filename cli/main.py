import requests
import yaml
import json
import fire
import tabulate
import pandas as pd

URL = 'https://05d2-173-63-132-127.ngrok.io'


def fetchall():
    """
    Returns JSON formatted data from the
    Cat API endpoint
    """
    COMMAND = '/api/v1/quotes/allfacts'
    url = URL + COMMAND
    resp = requests.get(url)
    return resp.text


def fetchall_in_json():
    """
    Returns all entries in json format
    : return: Returns all entries in json format
    """
    data = json.loads(fetchall())
    print(data)


def fetchall_in_yaml():
    """
    Returns all entries in yaml format
    : return: Returns all entries in yaml format
    """
    print(yaml.dump(yaml.load(fetchall(), Loader=yaml.FullLoader),
                    default_flow_style=False))


# TODO: Finish formatting the columns
def fetchall_in_table():
    """
    Returns all entries in table format
    : return: Returns all entries in table format
    """
    data = json.loads(fetchall())
    json_data = json.dumps(data)
    resp = pd.read_json(json_data)
    print(resp)


def delete_entry(id: int):
    """
    Deletes single entry based on id
    : param id: The id of the entry to delete
    : return: Deletes single entry based on id
    """
    COMMAND = '/api/v1/delete/'
    entry_id = id
    url = URL + COMMAND
    resp = requests.delete(url + str(entry_id))
    if resp.status_code == 200:
        print("Entry {} deleted successfully".format(entry_id))
    else:
        print("We couldn't delete the entry you specified.")


if __name__ == '__main__':
    fire.Fire({
        "output_in_json": fetchall_in_json,
        "output_in_yaml": fetchall_in_yaml,
        "output_in_table": fetchall_in_table,
        "delete_entry": delete_entry
    })
