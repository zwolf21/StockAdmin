import json, os
from datetime import date, datetime
from itertools import chain

from django.core.urlresolvers import reverse
from recordlib import RecordParser
from dateutil.parser import parse

APP_BASE_DIR = os.path.dirname(__file__)
COLLECT_LOG_FILE = os.path.join(APP_BASE_DIR, 'logs/collect.log')
MAX_COLLECT_LENGTH = 20
ord_types = {'st': '정기', 'ex': '추가', 'em': '응급', 'op': '퇴원', 'ch': '항암'}
ord_types_reverse = {'정기': 'st', '추가': 'ex', '응급':'em', '퇴원':'op', '항암':'ch'}

class LabelRecordParser:

	def __init__(self, json_path=COLLECT_LOG_FILE):
		self.json_path = json_path
		try:
			with open(json_path) as fp:
				self.label_history_list = json.loads(fp.read())
		except:
			self.label_history_list = []


	def save_queryset(self, agg, detail, ord_tp, form_data):
		today = date.today().strftime('%Y-%m-%d')
		seq_list = [row['seq'] for row in self.label_history_list if row['date'] == today and row['ord_tp'] == ord_types[ord_tp]]
		seq = max(seq_list) + 1 if seq_list else 0
		queryset = []
		recs = RecordParser(detail)

		today_queryset = [history for history in self.label_history_list if history['date'] == today]
		today_subqueryset = []

		for rec in today_queryset:
			collect_seq = rec['seq'] + 1
			for row in rec['records']:
				today_subqueryset.append((collect_seq, row['sub_object_list']))

		for item in agg:
			item['sub_object_list'] = recs.select('*', where = lambda row: row['ord_cd'] == item['ord_cd'], inplace=False).order_by(['ord_ymd', 'rcpt_dt']).records
			item['duplicated'] = False
			for sub in item['sub_object_list']:
				sub['duplicated'] = 0
				for cseq, today_sub_list in today_subqueryset:

					for today_sub in today_sub_list:
						sub_dup_save = sub.pop('duplicated')
						today_sub_save = today_sub.pop('duplicated')
						if sub == today_sub:
							sub['duplicated'] = cseq
							item['duplicated'] = True
						else:	
							sub['duplicated'] = sub_dup_save
						today_sub['duplicated'] = today_sub_save

			queryset.append(item)

		log = {
			'date' : today,
			'seq': seq,
			'ord_tp': ord_types[ord_tp],
			'form_data': form_data,
			'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			'records': queryset
		}
		self.label_history_list.append(log)
		with open(self.json_path, 'w') as fp:
			fp.write(json.dumps(self.label_history_list[-MAX_COLLECT_LENGTH:]))

		return log['records']
		
	def select_queryset(self, date=date.today().strftime('%Y-%m-%d'), seq=-1):
		queryset_list = [history for history in self.label_history_list if history['date'] == date and (history['seq'] == seq if seq!=-1 else True)]
		if not queryset_list:
			return
		if seq == -1:
			return queryset_list[seq]['records']
		return queryset_list[0]['records']

	def delete_queryset(self, ord_tp, date, seq):
		for idx, history in enumerate(self.label_history_list):
			if history['ord_tp'] == ord_types[ord_tp] and history['seq'] == int(seq) and history['date'] == date:
				self.label_history_list.pop(idx)
				with open(self.json_path, 'w') as fp:
					fp.write(json.dumps(self.label_history_list[-MAX_COLLECT_LENGTH:]))
				return 
		return

	def get_collect_object_list(self):
		ret = []
		for collect in self.label_history_list:

			s = '[{}]{} {}차({}건)'.format(collect['date'], collect['ord_tp'], collect['seq']+1, sum(len(rec['sub_object_list']) for rec in collect['records']))
			url = reverse('orderutils:labelcollect-history',
				 kwargs = {'date': collect['date'], 'seq': collect['seq'], 'ord_tp': ord_types_reverse[collect['ord_tp']]}
			)

			ret.append({'description': s, 'url': url})
		return ret[::-1]

	def select_collect(self, date, ord_tp, seq=-1):
		if not self.label_history_list:
			return []

		if seq == -1:
			ord_tp_history = [collect for collect in self.label_history_list if collect['ord_tp'] == ord_types[ord_tp]]
			return ord_tp_history[seq] if ord_tp_history else []

		for collect in self.label_history_list:
			if collect['seq'] == seq and collect['date'] == date and collect['ord_tp'] == ord_types[ord_tp]:
				return collect
		return []

	def get_last_collect(self, date=date.today().strftime('%Y-%m-%d')):
		ret = {}
		for collect in [collect for collect in self.label_history_list if collect['date'] == date]:
			ret[ord_types_reverse[collect['ord_tp']]] = collect['form_data']['end_t']

		return ret

	def clear_history(self):
		if os.path.exists(COLLECT_LOG_FILE):
			os.unlink(COLLECT_LOG_FILE)


# ret = load_collect_log()
# print(create_label_collect_queryset(ret['agg'], ret['detail']))
# l = LabelRecordParser()
# print(l.label_history_list)