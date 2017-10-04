import os, sys, re, datetime
from mimetypes import guess_type
from urllib.parse import quote
from wsgiref.util import FileWrapper
from email.header import Header, decode_header
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


from django.http import HttpResponse
from dateutil.parser import parse


def file_response(content, filename):
	ctype, encoding = guess_type(filename)
	response = HttpResponse(content, content_type=ctype or 'applicatioin/octet-stream')
	if encoding:
		response['Content-Encoding'] = encoding
	response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(quote(filename.encode('utf-8')))
	return response

#file_chunk_map -> {result_filename: chunk}
def gmail_attach_file(_from, _passwd, to_list, subject, content, file_chunk_map, host='smtp.gmail.com', port=587):
	outer = MIMEBase('multipart', 'mixed')
	outer['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
	outer['From'] = _from
	outer['To'] = ', '.join(to_list)
	outer.preamble = 'This is a multi-part message in MIME format.\n\n'
	outer.epilogue = ''
	msg = MIMEText(content.encode('utf-8'), _charset='utf-8')
	outer.attach(msg)

	for file, chunk in file_chunk_map.items():
		ctype, encoding = guess_type(file)
		maintype, subtype = ctype.split('/', 1)
		msg = MIMEApplication(chunk, _subtype=subtype)
		msg.add_header('Content-Disposition', 'attachment', filename=file)
		outer.attach(msg)

	s = smtplib.SMTP(host, port)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(_from, _passwd)
	s.sendmail(_from, to_list, outer.as_string())
	return s.quit()


def time_to_normstr(*time_values, to='date'):
	ret = []
	for value in time_values:
		if isinstance(value, (datetime.date, datetime.datetime)):
			time = value
		elif isinstance(value, str):
			try:
				time = parse(value)
			except ValueError:
				time = value
		else:
			time = value		
		ret.append(time)
	if to == 'date':
		ret = tuple(map(lambda time: time.strftime("%Y-%m-%d"), ret))
	else:
		ret = tuple(map(lambda time: time.strftime("%Y-%m-%d %H:%M:%S"), ret))

	if len(ret) == 1:
		return ret[0]
	return ret



