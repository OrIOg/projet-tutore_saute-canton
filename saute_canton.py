import request_canton
from graph import Country, Canton, Region
import random
from enum import Enum

class Direction(Enum):
    NORTH = "nord"
    SOUTH = "sud"
    EST = "est"
    WEST = "ouest"
    NORTH_WEST = "nord-ouest"
    NORTH_EST = "nored-est"
    SOUTH_WEST = "sud-ouest"
    SOUTH_EST = "sud-est"

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

    def get_starting_point(self, country: Country):
        random.seed()
        cantons = country.cantons.keys()

        starting_point = cantons[random.randint(len(cantons))]
        self.visited_cities.append(starting_point)
        self.visited_regions.append(starting_point.region)
        return starting_point

    def jump(self, canton : Canton):
        random.seed()
        nb_choice = len(Canton.neighbours)
        choices = canton.neighbours.keys()
        while(True):
            index = random.randint(nb_choice)
            choosen = canton.neighbours[choices[index]]
            if index not in self.visited_cities : 
                self.visited_cities.append(choosen)
                if choosen.region not in self.visited_regions:
                    self.visited_regions.append(choosen.region)
                return choosen


    def play(self, country : Country):
        city = self.get_starting_point(country)
        while(not self.arrived):
            if city.is_big : 
                self.arrived = True
                print("Arrived in a big city")
            else:
                if len(city.neighbours) <= 1 :
                    print("Plus de voisin dispo, Impossible")
                    break
                city = self.jump(city)
        
class FollowADirection(Voyager):

    def __init__(self, direction: Direction):
        self.visited_cities = []
        self.visited_regions = []
        self.arrived = False
        self.direction = direction

    def get_starting_point(self, country: Country):
        random.seed()
        cantons = country.cantons.keys()

        starting_point = cantons[random.randint(len(cantons))]
        self.visited_cities.append(starting_point)
        self.visited_regions.append(starting_point.region)
        return starting_point

    def compute_closest_city(self, coord, neighbors, neighbors_list):
        lat0, long0 = coord
        #a faire selon les cas ....
        choosen : Canton
        for city in neighbors_list:
            lat1, long1 = neighbors[city]




    def jump(self, canton : Canton):
        coord =  canton.coordinates
        neighbors = canton.neighbours
        neighbors_list = neighbors.keys()
        choosen : Canton
        while(True):
            if len(neighbors) == 0: 
                return 0
            else :
                choosen = self.compute_closest_city(coord, neighbors, neighbors_list)
                if choosen in self.visited_cities:
                    neighbors_list.remove(choosen.name)
                else : 
                    self.visited_cities.append(choosen)
                    if choosen.region not in self.visited_regions : 
                        self.visited_regions.append(choosen.region)
                    return choosen
        
    def play(self, country : Country):
    city = self.get_starting_point(country)
    while(not self.arrived):
        if city.is_big : 
            self.arrived = True
            print("Arrived in a big city")
        else:
            if len(city.neighbours) <= 1 :
                print("Plus de voisin dispo, Impossible")
                break
            city = self.jump(city)





