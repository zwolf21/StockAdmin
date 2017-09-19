import re
from listorm import Listorm

def filter_splited(records,  keyword, *columns, splitby=['space', 'nospace', 'digit'], exclude=False):
	'''splitby = ['space', 'nospace', 'digit']
	'''

	for sep in splitby:

		lst = Listorm(records)
		excluded = Listorm(records)

		ismatch = lambda keyword, text: re.search(keyword, text)

		if sep == 'space':
			tokkens = re.split('\s+', keyword)
		elif sep == 'nospace':
			ismatch = lambda keyword, text: re.search(re.sub('\s+','', keyword), re.sub('\s+','', text))
			tokkens = [keyword]
		elif sep == 'digit':
			tokkens = re.split('\d+', keyword) + re.findall('\d+', keyword)		

		for tok in tokkens:
			filtered = Listorm()
			for col in columns:
				filtered += lst.filter(where=lambda row: ismatch(tok, row[col]))
			if filtered:
				lst = filtered

		if lst:
			if exclude:
				for col in columns:
					colvalues = lst.unique(col)
					excluded = excluded.filter(where=lambda row: row[col] not in colvalues)
				return excluded
			else:
				return lst

	return Listorm()
		



userTable = [
    {'name': '네프라민 주 250ml(백)	', 'gender': 'M', 'age': 18, 'location': 'Korea'},
    {'name': '위너프 주 1435ml	', 'gender': 'M', 'age': 19, 'location': 'USA'},
    {'name': '위너프 페리 주 1450ml	', 'gender': 'F', 'age': 28, 'location': 'China'},
    {'name': '하모닐란 액 500ml', 'gender': 'M', 'age': 15, 'location': 'China'},
    {'name': '오마프원 페리 주 1448ml', 'gender': 'M', 'age': 29, 'location': 'Korea'},
    {'name': '멀티플렉스페리 주 1100ml', 'gender': 'M', 'age': 17, 'location': 'USA'},
]

for row in filter_splited(userTable, '위너프1435', 'name', exclude=False):
	print(row)


