import sqlite3
import re
import request_canton
import argparse
import sys

# Informations disponible: https://www.insee.fr/fr/information/4316069
START_COMMUNE = 1001
MAX_COMMUNE = 95690
BURST = 10

def drop_table(db: sqlite3.Connection, name):
    db.execute(f"DROP TABLE  IF EXISTS {name}")

#parse value of dic
def parse_uri(data):
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
    return(parse_uri(data["commune_de_France"]), data["commune_de_FranceLabel"]["value"], int(data["population"]["value"]),
            parse_uri(data["border"]), get_point(data["location"]["value"]), parse_uri(data["region"]), int(data["insee"]["value"]), 0)

#data is the big data list from the query
def insert_into_cities(db: sqlite3.Connection, data):
    nb_insertions = len(data)
    nb_digits = len(str(nb_insertions))
    for i, d in enumerate(data):
        sys.stdout.write(f"\tInserting {i:0{nb_digits}}/{nb_insertions}   \r")
        sys.stdout.flush()
        city = city_to_obj(d)
        db.execute("INSERT INTO cities (code, name, population, border, location, region, insee, distance) VALUES (?,?,?,?,?,?,?,?)", city)
    canton.commit()
    print()

def select_all_from(db, table):
    db.execute("SELECT * FROM " + table)
    return db.fetchall()

def main(db: sqlite3.Connection):
    db.execute(''' CREATE TABLE IF NOT EXISTS cities (code text, name text, population real, border text, location text, region text, insee INTEGER, distance INTEGER)''')
    db.commit()

    start = START_COMMUNE
    query = db.execute('''SELECT MAX(insee) FROM cities''').fetchone()
    if query and query[0]:
        start = query[0] + 1
        print("Cities already exists.")
        print(f"Nb cities  : {db.execute(''' SELECT count(DISTINCT code) FROM cities ''').fetchone()[0]}")
        print(f"Nb entries : {db.execute(''' SELECT count(code) FROM cities ''').fetchone()[0]}")


    while start < MAX_COMMUNE:
        nb = min(MAX_COMMUNE-start, BURST)
        print(f"Requesting: {start} => {start+nb}")
        r = request_canton.get_cities(request_canton.endpoint_url, start, nb)
        insert_into_cities(db, r["results"]["bindings"])
        start = db.execute(''' SELECT MAX(insee) FROM cities''').fetchone()[0] + 1
        print(f"Nb cities  : {db.execute(''' SELECT count(DISTINCT code) FROM cities ''').fetchone()[0]}")
        print(f"Nb entries : {db.execute(''' SELECT count(code) FROM cities ''').fetchone()[0]}")


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


if __name__ == "__main__":
    canton = sqlite3.connect("canton.db")

    parser = argparse.ArgumentParser(description='Manage DBs for the project.')
    actions = parser.add_argument_group(title="action", description="Action to perform with the DB.")
    parser.add_argument('--reset-all', help='Drop & Reinit the DB.', action='store_true', default=False)

    args = parser.parse_args()
    if args.reset_all:
        drop_table(canton, "cities")
        drop_table(canton, "region")

    main(canton)

    canton.close()