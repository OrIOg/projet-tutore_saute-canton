# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import re
import sys
import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
import sqlite3

endpoint_url = "https://query.wikidata.org/sparql"

query_city_only = """SELECT ?commune_de_France ?commune_de_FranceLabel ?departement ?region ?population ?location ?insee WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?commune_de_France wdt:P31 wd:Q484170.
  ?commune_de_France wdt:P1082 ?population.
  ?commune_de_France wdt:P625 ?location.
  ?commune_de_France wdt:P374 ?insee.
  FILTER(xsd:integer(?insee) >= %d).
  FILTER(xsd:integer(?insee) < %d).
  OPTIONAL {?commune_de_France wdt:P625 ?location.}
  OPTIONAL {?commune_de_France wdt:P131 ?departement.
  ?departement wdt:P31 wd:Q6465.}
  OPTIONAL {?departement wdt:P131 ?region.
  ?region wdt:P31 wd:Q36784.}
}"""

query_city_borders = """SELECT ?commune ?border WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  VALUES ?commune {
    wd:%s
  }
  ?commune wdt:P47 ?border.
  ?border wdt:P31 wd:Q484170.
  ?border wdt:P374 ?insee.
}"""

query2 = """
SELECT ?region ?regionLabel ?regionadj ?regionadjLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?region wdt:P31 wd:Q6465.
  ?region wdt:P47 ?regionadj
 }
"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_cities(endpoint_url, start_insee, end_insee):
  user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
  # TODO adjust user agent; see https://w.wiki/CX6
  sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
  sparql.setQuery(query_city_only % (start_insee, end_insee))
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()

def get_city_borders(endpoint_url, city_codes):
  user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
  # TODO adjust user agent; see https://w.wiki/CX6
  sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
  sparql.setQuery(query_city_borders % " wd:".join(city_codes))
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()




"""
results = get_results(endpoint_url, query1)
print(type(results["results"]["bindings"][0]))
for d in results["results"]["bindings"] :
  for k, i in d.items() :
    print(k + "->", end="")
    print(i)
  break


res = re.findall(r"[-+]?\d*\.\d+|\d+", 'Point(4.609722222 46.987222222)')
print(" ".join(res))"""

if __name__ == '__main__':
  data = get_cities(endpoint_url, 14118, 1)
  exit(data["results"]["bindings"][0]["commune_de_FranceLabel"]["value"] != "Caen")