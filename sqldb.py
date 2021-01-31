import sqlite3
import re
import request_canton

def reset_table(name):
    cursor.execute("DROP TABLE "+ name)

#parse value of dic 
def parse_uri(data):
    tokens = data["value"].split("/")
    return tokens[len(tokens) -1]

def get_point(point_str):
    res = re.findall(r"[-+]?\d*\.\d+|\d+", point_str)
    return " ".join(res)

#data is the big data list from the query
def insert_into_regions(data):
    print("begin insertion into regions")
    for d in data:
        region = parse_uri(d["region"])
        regionadj = parse_uri(d["regionadj"])

        cursor.execute("INSERT INTO regions (code, name, neighbour_code, neighbour_name) VALUES (?,?,?,?)",
                (region, d["regionLabel"]["value"], regionadj, d["regionadjLabel"]["value"]))
        canton.commit()
    print("insert into regions completed")

#data is the big data list from the query
def insert_into_cities(data):
    print("begin insertion into cities")
    for d in data:

        cursor.execute("INSERT INTO cities (code, name, population, border, location, region, distance) VALUES (?,?,?,?,?,?,?)",
            (parse_uri(d["commune_de_France"]), d["commune_de_FranceLabel"]["value"], int(d["population"]["value"]),
            parse_uri(d["border"]), get_point(d["location"]["value"]), parse_uri(d["region"]), 0))
        canton.commit()
    print("insert into cities completed")

def select_all_from(table):
    cursor.execute("SELECT * FROM " + table)
    return cursor.fetchall()

canton = sqlite3.connect("canton.db")
cursor = canton.cursor()

reset_table("cities")

cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='cities' ''')
if cursor.fetchone()[0] == 1 :
    print("table cities already created")
else: 
    print("creating table cities")
    cursor.execute(''' CREATE TABLE cities
        (code text, name text, population real, border text, location text, region text, distance INTEGER)''')
    canton.commit()
    print("table cities created")

r = request_canton.get_cities(request_canton.endpoint_url, 0)
insert_into_cities(r["results"]["bindings"])



reset_table("regions")
cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='regions' ''')
if cursor.fetchone()[0] == 1 :
    print("table regions already created")
else:
    print("creating table regions")
    cursor.execute(''' CREATE TABLE regions
        (code text, name text, neighbour_code text, neighbour_name text)''')
    canton.commit()
    print("table regions created")

r = request_canton.get_results(request_canton.endpoint_url, request_canton.query2)
insert_into_regions(r["results"]["bindings"])

canton.close()