from subdict import SubDict

from typing import Tuple, List, Dict


class Country:
	def __init__(self):
		self.regions: Dict[str, Region] = {}
		self.cantons: Dict[str, Canton] = {}

	def add_region(self, code: str, name: str, neighbours: List[str]):
		self.regions[code] = Region(self, code, name, neighbours)

	def add_canton(self, code: str, name: str, population: int, region: str, coordinates: Tuple[float, float], neighbours: List[str]):
		self.cantons[code] = Canton(
			self, code, name, population, self.regions[region], coordinates, neighbours)


class Canton:
	BIG_THRESOLD = 50000

	__slots__ = ['country', 'code', 'name',
              'population', 'region', 'coordinates', 'neighbours', 'is_big']

	def __init__(self, country: Country, code: str, name: str, population: int, region: str, coordinates: Tuple[float, float], neighbours: List[str]):
		self.country = country
		self.code: str = code
		self.name: str = name
		self.population: int = population

		self.region: str = region
		self.coordinates: Tuple[float, float] = coordinates
		self.neighbours: SubDict = SubDict(country.cantons, neighbours)
		self.is_big = self.population >= self.BIG_THRESOLD


class Region:

	__slots__ = ['country', 'code', 'name', 'neighbours']

	def __init__(self, country: Country, code: str, name: str, neighbours: List[str]):
		self.code: str = code
		self.name: str = name
		self.country: str = country
		self.neighbours: SubDict = SubDict(country.regions, neighbours)


