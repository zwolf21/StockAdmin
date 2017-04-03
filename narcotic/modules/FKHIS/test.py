import codecs
import re
import filecmp
'requests/PsyStock.req'

psy = 'C:\\Users\\HS\\Desktop\\PsyStock.req'
narc = 'C:\\Users\\HS\\Desktop\\NarcStock.req'

with codecs.open(psy, 'rb') as fp:
	psy=fp.read()

with codecs.open(narc, 'rb') as fp:
	narc=fp.read()


psy_q = b'\x00\x00\x00\x012'
narc_pat = re.compile(b'\x00\x00\x00\x011')

# narc = narc_pat.sub(psy_q, narc)

print(narc_pat.findall(narc))



