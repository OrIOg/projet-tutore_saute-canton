import collections.abc
from typing import Tuple


class SubDict(collections.abc.MutableMapping):
	def __init__(self, refDict: dict, valid_keys: Tuple[str]):
		self._dict = refDict
		self._valid_keys = valid_keys

	def __len__(self):
		return len(self._valid_keys)

	def __length_hint__(self):
		return NotImplementedError()

	def __getitem__(self, index):
		if index not in self._valid_keys:
			return KeyError(f"Invalid key: {index}.")
		return self._dict[index]

	def __setitem__(self, index, value):
		return KeyError("Can't set in sub dict.")

	def __delitem__(self, index):
		return KeyError("Can't delete in sub dict.")

	def __missing__(self, index):
		return KeyError(f"Invalid key: {index}.")

	def keys(self):
		return list(self._valid_keys)

	def values(self):
		return [self._dict[key] for key in self._valid_keys]

	def __iter__(self):
		return iter(self.keys())

	def __contains__(self, key):
		return key in self._valid_keys
