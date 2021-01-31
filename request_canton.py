# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import re
import sys
import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
import sqlite3

endpoint_url = "https://query.wikidata.org/sparql"

query1 = """SELECT ?commune_de_France ?commune_de_FranceLabel ?population ?border ?location ?region WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?commune_de_France wdt:P31 wd:Q484170.
  ?commune_de_France wdt:P1082 ?population.
  ?commune_de_France wdt:P47 ?border.
  ?commune_de_France wdt:P625 ?location.
  ?region wdt:P31 wd:Q6465.
}

OFFSET %s
LIMIT 20000
"""

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

def get_cities(endpoint_url, offset):
  user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
  # TODO adjust user agent; see https://w.wiki/CX6
  sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
  sparql.setQuery(query1 % (offset))
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