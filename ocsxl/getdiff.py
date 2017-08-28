import argparse, sys, re, os
from datetime import datetime
from collections import OrderedDict
from io import BytesIO
import listorm as ls
from dateutil import parser
import xlsxwriter

def write_CD(context, ws, column_orders):
	ws.write_row(0,0,column_orders)
	for r, sub in enumerate(context):
		row_values = [sub.rows[k] for k in column_orders]
		ws.write_row(r+1, 0, row_values)


def write_updated(context, ws, pk, column_orders=None, extras=None):
	line_feed_acc = 0
	records = []
	for r, updated in enumerate(context):
		record_before = ls.Scheme({k:updated.before[k] for k in updated.where+(extras or [])})
		record_before['변경전후'] = '변경전'
		record_before[pk] = updated.pk
		record_after = ls.Scheme({k:updated.after[k] for k in updated.where+(extras or [])})
		record_after['변경전후'] = '변경후'
		record_after[pk] = updated.pk
		records.append(record_before)
		records.append(record_after)
	
	if not records:
		return

	lst = ls.Listorm(records)
	left =  ['변경전후']+[pk]  + (extras or [])  
	right = [col for col in column_orders if col in lst[0]]
	selects = left + right

	if ws is None:
		return [OrderedDict((key, row[key]) for key in selects) for row in lst]


	selects = list(OrderedDict.fromkeys(selects))
	ws.write_row(0, 0, selects)

	for r, record in enumerate(lst):
		row_values = [record.get(k) for k in selects]
		ws.write_row(r+1, 0, row_values)


def compare_contents(content_before, content_after, pk, extras, to_context=False):
	lst_before = ls.read_excel(file_contents=content_before)
	lst_after = ls.read_excel(file_contents=content_after)
	inout_map = {'1': '원외', '2': '원외', '3':'원내/원외'}
	column_orders = lst_before.column_orders
	lst_before = lst_before.map(**{'원내/원외 처방구분': inout_map.get})
	lst_after = lst_after.map(**{'원내/원외 처방구분': inout_map.get})
	
	if to_context:
		lst_before = lst_before.add_columns(drug_name=lambda row: row['약품명(한글)'], inout=lambda row: row['원내/원외 처방구분'])
		lst_after = lst_after.add_columns(drug_name=lambda row: row['약품명(한글)'], inout=lambda row: row['원내/원외 처방구분'])
		changes = lst_before.get_changes(lst_after, pk=pk)
		return changes

	changes = lst_before.get_changes(lst_after, pk=pk)
	output = BytesIO()

	wb = xlsxwriter.Workbook(output)
	ws_added = wb.add_worksheet('추가된항목')
	ws_deleted = wb.add_worksheet('삭제된항목')
	ws_updated = wb.add_worksheet('변경된항목')

	write_CD(changes.added, ws_added, lst_before.column_orders)
	write_CD(changes.deleted, ws_deleted, lst_before.column_orders)
	write_updated(changes.updated, ws_updated, pk, column_orders=lst_before.column_orders, extras=extras)

	wb.close()

	return output.getvalue()



def compare(before, after, pk, extras, start):
	fname_before = os.path.basename(before)
	fname_after = os.path.basename(after)

	fname_before, ext = os.path.splitext(fname_before)
	fname_after, ext = os.path.splitext(fname_after)

	filename = '[Source {}][Dest {}].xlsx'.format(fname_before, fname_after)

	lst_before = ls.read_excel(before)
	lst_after = ls.read_excel(after)

	changes = lst_before.get_changes(lst_after, pk=pk)

	wb = xlsxwriter.Workbook(filename)
	ws_added = wb.add_worksheet('Added')
	ws_deleted = wb.add_worksheet('Deleted')
	ws_updated = wb.add_worksheet('Updated')

	write_CD(changes.added, ws_added, lst_before.column_orders)
	write_CD(changes.deleted, ws_deleted, lst_before.column_orders)
	write_updated(changes.updated, ws_updated, pk, column_orders=lst_before.column_orders, extras=extras)

	wb.close()

	if start:
		try:
			os.startfile(filename)
		except:
			return

def main(*args):
	compare(*args)



if __name__ == '__main__':

	argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	argparser.add_argument('files', help='put 2 files path by modified sequence', nargs=2)
	argparser.add_argument('-f', '--before', help='Before Modified')
	argparser.add_argument('-l', '--after', help='After Modified')
	argparser.add_argument('-k', '--pk', help='Set primary key')
	argparser.add_argument('-e', '--extras', help='Extra Columns for Identifying on Updated List', nargs='+')
	argparser.add_argument('-K', '--PK', help='Set Primary key and start file')
	args = argparser.parse_args()

	if (args.pk or args.PK) is None:
		print('Primary Key is needed!')
		sys.exit(0)

	before, after = args.files or (args.before, args.after)
	main(before, after, args.pk or args.PK , args.extras, args.PK)

