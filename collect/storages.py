import os, json, sys, datetime
from pprint import pprint
from operator import itemgetter

from listorm import Listorm

COLLECT_FILE = os.path.join(os.path.dirname(__file__), 'caches/collects.json')
STATIC_INFO_FILE = os.path.join(os.path.dirname(__file__), 'caches/configs.json')
MAX_OBJECT_LIST_LENGTH = 40



class CollectStorage(object):
	
	def __init__(self, filepath, max_object_list_length=MAX_OBJECT_LIST_LENGTH):
		self.path = filepath
		self.max_object_list_length = max_object_list_length
		self._get_or_create_dir(self.path)
		self._load()

	def _get_or_create_dir(self, path):
		try:
			if os.path.isdir(path):
				os.makedirs(path)
			else:
				path = os.path.dirname(path)
				os.makedirs(path)
		except:
			return

	def _load(self):
		if os.path.isfile(self.path):
			with open(self.path) as fp:
				self.object_list = Listorm(json.loads(fp.read()))
		else:
			self.object_list = Listorm()

	def save(self, object=None, commit=True):
		if object:
			self.object_list.append(object)
		if commit:
			with open(self.path, 'w') as fp:
				object_list = self.object_list[-self.max_object_list_length:]
				data = json.dumps(object_list, indent=4)
				fp.write(data)
			return
		return self.object_list

	def delete(self, slug):
		self.object_list = self.object_list.filter(lambda row: row.slug != slug)
		self.save()
	
	def clear(self):
		self.object_list = Listorm()
		self.save()

	def get(self, slug):
		return self.object_list.filterand(slug=slug).first

	def get_object_list(self):
		return Listorm(self.object_list[::-1])

	def get_latest(self, **kwargs):
		for key, val in kwargs.items():
			if key == 'date':
				kwargs[key] = time_to_normstr(val)
		latest = self.object_list.filterand(**kwargs).top('seq')
		return latest



class StaticStorage(CollectStorage):
	initial = [
		{'kind': 'LABEL', 'extras':'', 'excludes':''},
		{'kind': 'INJ', 'extras':'', 'excludes':''},
		{'kind': 'NUT', 'extras':'', 'excludes':''},
	]

	def __init__(self, filepath=STATIC_INFO_FILE):
		super(StaticStorage, self).__init__(filepath)

	def _load(self):
		if os.path.isfile(self.path):
			with open(self.path) as fp:
				self.object_list = Listorm(json.loads(fp.read()))
		else:
			with open(self.path, 'w') as fp:
				fp.write(json.dumps(self.initial, indent=4))
			self._load()

	def save(self, kind, excludes=None, extras=None, **kwargs):
		if excludes is not None:
			self.object_list.update(excludes=excludes, where=lambda row:row.kind==kind)
		if extras is not None:
			self.object_list.update(extras=extras, where=lambda row:row.kind==kind)

		with open(self.path, 'w') as fp:
			fp.write(json.dumps(self.object_list, indent=4))

	def get(self, kind=None):
		obj = self.object_list.filterand(kind=kind).first if kind else self.object_list
		return obj

