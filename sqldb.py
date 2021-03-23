import sqlite3
import re
from typing import List
import request_canton
import argparse
import sys

# Informations disponible: https://www.insee.fr/fr/information/4316069
START_COMMUNE = 1001
MAX_COMMUNE = 95690
BURST = 1000
SMALL_BURST = 100

def drop_table(db: sqlite3.Connection, name):
    db.execute(f"DROP TABLE  IF EXISTS {name}")
    db.commit()

#parse value of dic
def parse_uri(data):
    if data == None: return ""
    tokens = data["value"].split("/")
    return tokens[len(tokens) -1]

def get_point(point_str):
    res = re.findall(r"[-+]?\d*\.\d+|\d+", point_str)
    return " ".join(res)

#data is the big data list from the query
def insert_into_regions(db: sqlite3.Connection, data):
    print("begin insertion into regions")
    for d in data:
        region = parse_uri(d["region"])
        regionadj = parse_uri(d["regionadj"])

        db.execute("INSERT INTO regions (code, name, neighbour_code, neighbour_name) VALUES (?,?,?,?)",
                (region, d["regionLabel"]["value"], regionadj, d["regionadjLabel"]["value"]))
        canton.commit()
    print("insert into regions completed")

def city_to_obj(data):
    return(parse_uri(data["commune_de_France"]),
           data["commune_de_FranceLabel"]["value"],
           parse_uri(data.get("departement", None)),
           parse_uri(data.get("region", None)),
           int(data["population"]["value"]),
           get_point(data["location"]["value"]),
           -1)

#data is the big data list from the query
def insert_into_cities(db: sqlite3.Connection, data):
    nb_insertions = len(data)
    nb_digits = len(str(nb_insertions))
    duplicates = set()
    for i, d in enumerate(data):
        sys.stdout.write(f"\tInserting {i:0{nb_digits}}/{nb_insertions}   \r")
        sys.stdout.flush()
        city = city_to_obj(d)
        if(city[0] in duplicates): continue
        duplicates.add(city[0])
        db.execute("INSERT INTO cities (code, name, departement, region, population, location, distance) VALUES (?,?,?,?,?,?,?)", city)
    canton.commit()
    print()

def select_all_from(db: sqlite3.Connection, table):
    rs = db.execute("SELECT * FROM " + table)
    return rs.fetchall()

def init(db: sqlite3.Connection):
    db.execute(''' CREATE TABLE IF NOT EXISTS cities (code text, name text, departement text, region text, population INTEGER, location text, distance INTEGER)''')
    db.execute(''' CREATE TABLE IF NOT EXISTS cities_borders (code text, neighbour text)''')
    db.commit()

def query_cities(db: sqlite3.Connection):
    start = START_COMMUNE
    while start < MAX_COMMUNE:
        r = request_canton.get_cities(request_canton.endpoint_url, start, start+BURST)
        insert_into_cities(db, r["results"]["bindings"])
        print(f"Nb cities  : {db.execute(''' SELECT count(DISTINCT code) FROM cities ''').fetchone()[0]}")
        print(f"Nb entries : {db.execute(''' SELECT count(code) FROM cities ''').fetchone()[0]}")
        start += BURST
    #insert_into_cities(db, r["results"]["bindings"])


    """
    drop_table("regions")
    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='regions' ''')
    if cursor.fetchone()[0] == 1 :
        print("table regions already created")
    else:
        print("creating table regions")
        cursor.execute(''' CREATE TABLE regions
            (code text, name text, neighbour_code text, neighbour_name text)''')
        db.commit()
        print("table regions created")

    r = request_canton.get_results(request_canton.endpoint_url, request_canton.query2)
    insert_into_regions(r["results"]["bindings"])

    db.close()"""

def query_cities_neighbors(db: sqlite3.Connection):
    data = db.execute(''' SELECT code FROM cities ''').fetchall()
    nb_cities = len(data)
    nb_digits = len(str(nb_cities))

    for i in range(0, nb_cities, SMALL_BURST):
        codes = [code[0] for code in data[i:i+SMALL_BURST]]
        r = request_canton.get_city_borders(request_canton.endpoint_url, codes)["results"]["bindings"]
        for res in r:
            db.execute("INSERT INTO cities_borders (code, neighbour) VALUES (?,?)", (parse_uri(res["commune"]), parse_uri(res["border"])))
        print(f"\t[{(1+i):0{nb_digits}}/{nb_cities}] Inserting {len(r)} neighbors")
        db.commit()
    print()

def get_db_connection():
    return sqlite3.connect("canton.db")

def get_cities(db: sqlite3.Connection, raw=False):
    cities: List[List] = select_all_from(db, "cities")
    if not raw:
        for i, city in enumerate(cities):
            city = list(city)
            city[4] = int(city[4])
            dst = int(city[6])
            location = city[5].split(' ')
            city[5] = float(location[0])
            city[6] = float(location[1])
            city.append(dst)
            cities[i] = city
    return cities

def get_borders(db: sqlite3.Connection):
    return select_all_from(db, "cities_borders")

if __name__ == "__main__":
    canton = sqlite3.connect("canton.db")

    parser = argparse.ArgumentParser(description='Manage DBs for the project.')
    actions = parser.add_argument_group(title="action", description="Action to perform with the DB.")
    parser.add_argument('--reset-all', help='Drop & Reinit the DB.', action='store_true')
    parser.add_argument('--reset-cities', help='Drop & Reinit the cities.', action='store_true')
    parser.add_argument('--reset-cn', help='Drop & Reinit cities neighbors the DB.', action='store_true')
    parser.add_argument('--get-cities', help='Get cities.', action='store_true')
    parser.add_argument('--get-cn', help='Get cities neighbors.', action='store_true')

    args = parser.parse_args()
    if args.reset_all:
        drop_table(canton, "cities")
        drop_table(canton, "cities_borders")
        drop_table(canton, "region")

    if args.reset_cities:
        drop_table(canton, "cities")

    if args.reset_cn:
        drop_table(canton, "cities_borders")

    init(canton)

    if args.get_cities:
        query_cities(canton)

    if args.get_cn:
        query_cities_neighbors(canton)

    canton.close()