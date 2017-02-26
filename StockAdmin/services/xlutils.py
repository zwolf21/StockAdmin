import os, smtplib
from io import BytesIO
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from email.header import Header, decode_header
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import xlsxwriter

def excel_output(records):
    output = BytesIO()
    wb = xlsxwriter.Workbook(output, {'inmemory': True, 'remove_timezone': True})
    ws = wb.add_worksheet()
    hdr = records[0].keys()
    ws.write_row(0,0, hdr)
    for i, row in enumerate(records):
        ws.write_row(i+1, 0, map(str, row.values()))
    wb.close()
    return output.getvalue()



#excel_chunk_map -> {result_filename: chunk}
def excel_gmail_send(_from, _passwd, to_list, subject, content, excel_chunk_map, host='smtp.gmail.com', port=587):
	outer = MIMEBase('multipart', 'mixed')
	outer['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
	outer['From'] = _from
	outer['To'] = ', '.join(to_list)
	outer.preamble = 'This is a multi-part message in MIME format.\n\n'
	outer.epilogue = ''
	msg = MIMEText(content.encode('utf-8'), _charset='utf-8')
	outer.attach(msg)

	for file, chunk in excel_chunk_map.items():
		ctype = 'application/vnd.ms-excel'
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


