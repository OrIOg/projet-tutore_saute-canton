import request_canton
from graph import Country, Canton, Region
import random
from enum import Enum

import sqldb
import sqlite3

import pickle
import os
from io import StringIO

class Direction(Enum):
    NORTH = ("nord", (0, -000))
    SOUTH = ("sud", (0, -1000))
    EST = ("est", (-1000, 0))
    WEST = ("ouest", (1000, 0))
    NORTH_WEST = ("nord-ouest", (1000, 1000))
    NORTH_EST = ("nored-est", (-1000, 1000))
    SOUTH_WEST = ("sud-ouest", (1000, -1000))
    SOUTH_EST = ("sud-est", (-1000, -1000))

class VoyagerMeta(type):
        def __instancecheck__(cls, instance):
            return cls.__subclasscheck__(type(instance))

        def __subclasscheck__(cls, subclass):
            return (hasattr(subclass, 'visited_cities') and 
                    hasattr(subclass, 'visited_regions') and 
                    hasattr(subclass, 'arrived') and 
                    callable(subclass.jump) and
                    callable(subclass.get_starting_point) and
                    callable(subclass.play))

class Voyager(metaclass=VoyagerMeta):
    pass


class RandomDirection(Voyager):


    def __init__(self):
        self.visited_cities = []
        self.visited_regions = []
        self.arrived = False
        self.file = open("randomstat.csv", "at")

    def get_starting_point(self, country: Country):
        random.seed()
        cantons = list(country.cantons.keys())
        k = cantons[random.randint(0,len(cantons) -1)]
        starting_point = country.cantons[k]

        self.visited_cities.append(starting_point.name)
        self.visited_regions.append(starting_point.region)
        return starting_point 


    def tooMuchOccurence(self, choices):
        for city_name in choices:
            if city_name in self.visited_cities and self.visited_cities.count(choosen.name) <= 3: 
                return False

        return True

    
    def jump(self, canton : Canton):
        random.seed()
        nb_choice = len(canton.neighbours)
        choices = list(canton.neighbours.keys())
        """for key in canton.neighbours.keys():
            if key == None:
                print("probleme")
            else:
                print(key, canton.neighbours[key].name)"""
        while(True):
            index = random.randint(0, nb_choice-1)
            to_choose = choices[index]
            print("index:",  index , "nb choice = ", nb_choice, "o_choose:", to_choose)
            ngh = ""
            for n in canton.neighbours.keys():
                ngh += "," + n
            print(ngh)
            choosen = canton.neighbours[to_choose]
            print("choosen = ", choosen)
            if choosen.name not in self.visited_cities or self.visited_cities.count(choosen.name) <= 3: 
                self.visited_cities.append(choosen.name)
                if choosen.region not in self.visited_regions:
                    self.visited_regions.append(choosen.region)
                return choosen
            elif self.tooMuchOccurence(choices): 
                return None
            

    def play(self, country : Country):
        city = self.get_starting_point(country)
        nb_jump = 0
        while(not self.arrived):
            if city.is_big : 
                self.arrived = True
                print("Arrived in a big city")
            else:
                if len(city.neighbours) < 1 :
                    print("Plus de voisin dispo, Impossible")
                    break
                city = self.jump(city)
                if city == None:
                    break

                nb_jump += 1
        things_to_write = ("random, ", nb_jump, ",", self.arrived, ","
                            , len(self.visited_cities), ",",len(self.visited_regions)
                            , self.visited_cities[0], self.visited_cities[-1])
        to_write = ''.join([str(t) for t in things_to_write])
        self.file.write(to_write)
        
class FollowADirection(Voyager):

    def __init__(self, direction: Direction):
        self.visited_cities = []
        self.visited_regions = []
        self.arrived = False
        self.direction = direction
        self.file = open("followstat.csv", "at")

    def get_starting_point(self, country: Country):
        random.seed()
        cantons = country.cantons.keys()

        starting_point = cantons[random.randint(0, len(cantons) -1)]
        self.visited_cities.append(starting_point.name)
        self.visited_regions.append(starting_point.region)
        return starting_point

    def compute_closest_city(self, coord, neighbors):
               
        best_city : Canton
        best_lg, best_lt = coord
        for city in neighbors.values():
            cur_lg, cur_lt = city.coordinates
            if self.direction == Direction.EST :           
                if cur_lg <  best_lg : 
                    best_lg  = cur_lg
                    best_city = city
            
            elif self.direction == Direction.NORTH:
                if cur_lt >  best_lt : 
                    best_lt  = cur_lt
                    best_city = city
            elif self.direction == Direction.WEST:
                if cur_lg >  best_lg : 
                    best_lg  = cur_lg
                    best_city = city
            elif self.direction == Direction.SOUTH:
                if cur_lt <  best_lt : 
                    best_lt  = cur_lt
                    best_city = city
            elif self.direction == Direction.NORTH_EST:
                if cur_lg <  best_lg  or cur_lt >  best_lt : 
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city
            elif self.direction == Direction.NORTH_WEST:
                if cur_lt + cur_lg >  best_lt + best_lt: 
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city
            elif self.direction == Direction.SOUTH_EST:
                if cur_lt + cur_lg <  best_lt + best_lt: 
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city
            else :
                if cur_lg >  best_lg  or cur_lt <  best_lt : 
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city

        return best_city




    def jump(self, canton : Canton):
        coord =  canton.coordinates
        neighbors = canton.neighbours
        choosen : Canton
        while(True):
            if len(neighbors) == 0: 
                return None
            else :
                choosen = self.compute_closest_city(coord, neighbors)
                self.visited_cities.append(choosen)
                if choosen.region not in self.visited_regions : 
                    self.visited_regions.append(choosen.region)
                return choosen
        
    def play(self, country : Country):
        city = self.get_starting_point(country)
        nb_jump = 0
        while(not self.arrived):
            if city.is_big : 
                self.arrived = True
                print("Arrived in a big city")
            else:
                if len(city.neighbours) < 1 :
                    print("Plus de voisin dispo, Impossible")
                    break
                city = self.jump(city)
                if city == None:
                    break
            nb_jump += 1

        things_to_write = (self.direction, ",",nb_jump, ",", self.arrived, ","
                            , len(self.visited_cities), ",",len(self.visited_regions)
                            , self.visited_cities[0], self.visited_cities[-1])
        to_write = ''.join([str(t) for t in things_to_write])
        self.file.write(to_write)



if __name__ == '__main__' :


    if os.path.exists('france.p'):
        france = pickle.load(open("france.p", "rb"))

    else:
        canton = sqlite3.connect("canton.db")
        
        print("connected")
        sqldb.init(canton)
        cities  = sqldb.get_cities(canton)
        borders = sqldb.get_borders(canton)
        
        print(cities[1])

        france = Country()
        border_index = []
        border_index.extend(range(len(borders)))

        for city in cities : 
            code = city[0]
            print(code)
            name = city[1]
            region = city[2]
            dep = city[3]
            pop = int(city[4])
            coord = (city[5], city[6])
            neigh = []
            for i in border_index : 
                if borders[i][0] == code :
                    neigh.append(borders[i][1])
                    border_index.remove(i)
            france.add_canton(code, name, pop, region, coord, neigh)
        print(len(france.cantons))
        pickle.dump(france, open("france.p", "xb"))

    for i in range(100):
        r_player = RandomDirection()
        r_player.play(france)

