import request_canton
from graph import Country, Canton, Region
import random
from enum import Enum
import argparse

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
    NORTH_EST = ("nord-est", (-1000, 1000))
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
        self.file = open("resultats/randomstat.csv", "at",  encoding="utf-8")

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
                break
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
                                ,",", self.visited_cities[0], ",", self.visited_cities[-1], "\n")
        to_write = ''.join([str(t) for t in things_to_write])
        self.file.write(to_write)

    def copy(self):
        return RandomDirection()
        
class FollowADirection(Voyager):

    def __init__(self, direction: Direction):
        self.visited_cities = []
        self.visited_regions = []
        self.arrived = False
        self.direction = direction
        d = direction.value[0]
        name = "resultats/followstat_" + d
        self.file = open(name +".csv", "at")

    def get_starting_point(self, country: Country):
        random.seed()
        starting_point = random.choice(list(country.cantons.values()))

        self.visited_cities.append(starting_point.name)
        self.visited_regions.append(starting_point.region)
        return starting_point 

    def choose_random_city(self, neighbors):
        random.seed()
        return random.choice(list(neighbors.values()))


    def compute_closest_city(self, coord, neighbors):
               
        best_lg, best_lt = coord
        token = False
        for city in neighbors.values():
            cur_lg, cur_lt = city.coordinates
            if self.direction == Direction.EST :           
                if cur_lg <  best_lg : 
                    best_lg  = cur_lg
                    best_city = city
                    token = True
            elif self.direction == Direction.NORTH:
                if cur_lt >  best_lt : 
                    best_lt  = cur_lt
                    best_city = city
                    token = True
            elif self.direction == Direction.WEST:
                if cur_lg >  best_lg : 
                    best_lg  = cur_lg
                    best_city = city
                    token = True
            elif self.direction == Direction.SOUTH:
                if cur_lt <  best_lt : 
                    best_lt  = cur_lt
                    best_city = city
                    token = True
            elif self.direction == Direction.NORTH_EST:
                if cur_lg <  best_lg  != cur_lt >  best_lt : #semble bon
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city
                    token = True
            elif self.direction == Direction.NORTH_WEST: #c bon
                if cur_lt + cur_lg >  best_lt + best_lg: 
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city
                    token = True
            elif self.direction == Direction.SOUTH_EST: #c bon
                if cur_lt + cur_lg <  best_lt + best_lg: 
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city
                    token = True
            else :
                if cur_lg >  best_lg  != cur_lt <  best_lt : #pareillement
                    best_lg  = cur_lg
                    best_lt = cur_lt
                    best_city = city
                    token = True
        if(not token): 
            l_name = []
            neigh = []
            for city in neighbors.values():
                neigh.append(city.name)

            while(True):
                best_city = self.choose_random_city(neighbors)
                if(not best_city.name in self.visited_cities) and best_city.name not in l_name:
                    break;
                if all(city in l_name for city in neigh):
                    return None
                l_name.append(best_city.name)
                #print(best_city.name)
        print(best_city.name)
        return best_city




    def jump(self, canton : Canton):
        coord =  canton.coordinates
        neighbors = canton.neighbours
        choosen : Canton
        if len(neighbors) == 0: 
            return None
        else :
            choosen = self.compute_closest_city(coord, neighbors)
            if choosen == None:
                return None
            self.visited_cities.append(choosen.name)
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
                break
            else:
                if len(city.neighbours) < 1 :
                    print("Plus de voisin dispo, Impossible")
                    break
                city = self.jump(city)
                if city == None:
                    break
            nb_jump += 1
        #partie où on écrit
        things_to_write = (self.direction, ",",nb_jump, ",", self.arrived, ","
                           , len(self.visited_cities), ",",len(self.visited_regions)
                            , ",",self.visited_cities[0], ",", self.visited_cities[-1], "\n")
        to_write = ''.join([str(t) for t in things_to_write])
        self.file.write(to_write)

    def copy(self):
        return FollowADirection(self.direction)



if __name__ == '__main__' :


    if os.path.exists('france.p'):
        france = pickle.load(open("france.p", "rb"))

    else:
        canton = sqlite3.connect("canton.db")
        
        print("connected")
        sqldb.init(canton)
        cities  = sqldb.get_cities(canton)
        borders = sqldb.get_borders(canton)
        print(cities[0])
        print(borders[1])
        france = Country()
        border_index = []
        border_index.extend(range(len(borders)))

        for city in cities : 
            code = city[0]
            name = city[1]
            region = city[2]
            dep = city[3]
            pop = int(city[4])
            coord = (city[5], city[6])
            neigh = []
            """for i in border_index : 
                if borders[i][0] == code :
                    neigh.append(borders[i][1])
                    border_index.remove(i)"""
            france.add_canton(code, name, pop, region, coord, neigh)
            print(len(france.cantons))

        list_cities = france.cantons.keys()
        for city in list_cities:
            neigh = []
            for i in border_index : 
                if borders[i][0] == city and borders[i][1] in list_cities:
                    neigh.append(borders[i][1])
                    border_index.remove(i)
            france.add_neighbours_to_canton(city, neigh)

        #all neighbours completed
        pickle.dump(france, open("france.p", "xb"))


    d = "for direction bot"
    parser = argparse.ArgumentParser()
    parser.add_argument("nb", type=int,
                    help="loop number")
    parser.add_argument("-random", "-r", action="store_true", help="for random bot")
    parser.add_argument("-north", "-n", action="store_true", help=d)
    parser.add_argument("-south", "-s", action="store_true", help=d)
    parser.add_argument("-est", "-e", action="store_true", help=d)
    parser.add_argument("-west", "-w", action="store_true", help=d)
    parser.add_argument("-north_est", "-n_e", action="store_true", help=d)
    parser.add_argument("-north_west", "-n_w", action="store_true", help=d)
    parser.add_argument("-south_est", "-s_e", action="store_true", help=d)
    parser.add_argument("-south_west", "-s_w", action="store_true", help=d)

    args = parser.parse_args()
    if args.random:
        player = RandomDirection()
    elif args.north:
        player = FollowADirection(Direction.NORTH)
    elif args.south:
        player = FollowADirection(Direction.SOUTH)
    elif args.est:
        player = FollowADirection(Direction.EST)
    elif args.west:
        player = player = FollowADirection(Direction.WEST)
    elif args.north_est:
        player = FollowADirection(Direction.NORTH_EST)
    elif args.north_west:
        player = FollowADirection(Direction.NORTH_WEST)
    elif args.south_est:
        player = player = FollowADirection(Direction.SOUTH_EST)
    else:
        player = player = FollowADirection(Direction.SOUTH_WEST)


    for i in range(args.nb):
        player.play(france)
        player = player.copy()

