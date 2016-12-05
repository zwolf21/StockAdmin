from .models import Info
import os, csv, sys, math
import xlrd, xlwt
from django.conf import settings
from io import TextIOWrapper, StringIO
from django.http import HttpResponse



def float2int(value):
    try:
        return math.floor(float(value))
    except ValueError:
        return value


def dict2csv(queryset, szfile):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachmemt; filename="{}"'.format(szfile)
    queryset = queryset.values()
    writer = csv.DictWriter(response, queryset.first().keys())
    writer.writeheader()
    for dic in queryset:
        writer.writerow(dic)
    return response

def dict2xl(queryset, szfile):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachmemt; filename="{}"'.format(szfile)
    queryset = queryset.values()
    fields = queryset.first().keys()
    wb = xlwt.Workbook()
    sht = wb.add_sheet('sheet1')
    
    for c, data in enumerate(fields):
        sht.write(0,c,data)
   
    for r, query in enumerate(queryset):
        for c, val in enumerate(query.values()):
            sht.write(r+1, c, str(val))

    wb.save(response)
    return response




    # col_index = dict(zip(queryset.first().keys(),range(len(queryset.first()))))


    




def xl2csv(xlfp, csvname='temp.csv'):
    wb = xlrd.open_workbook(file_contents=xlfp.read())
    sh = wb.sheet_by_index(0)

    with open(csvname, 'w') as csvfp:
    	writer = csv.writer(csvfp)
    	for nrow in range(sh.nrows):
            cur_row = sh.row_values(nrow)
            writer.writerow(list(map(float2int, cur_row)))
    return open(csvname)


def csv_update(request):

    fp = request.FILES['csv']
    fn, ext = os.path.splitext(fp.name)
    context = {
        'success_count': 0,
        'failure_count': 0,
        'failures': [],
        'created': [],
        'updated': [],
        'noupdated': [],
        'preupdated': []
    }

    if ext == '.csv':
        fp = TextIOWrapper(fp.file, encoding=request.encoding)
    elif ext in ('.xlsx', '.xls'):
        fp = xl2csv(fp)
    else:
        return context

    reader = csv.DictReader(fp)
    for row in reader:
       try:
            obj, created = Info.objects.get_or_create(
                edi=row['edi'], defaults=row)
       except:
            type_err, val_err, trcbk = sys.exc_info()
            context['failure_count'] += 1
            context['failures'].append({'error_type': type_err.__name__, 'error_value': val_err, 'name': row.get('name'), 'edi': row.get('edi')})
       else:
            context['success_count'] += 1
            if created:
                context['created'].append(obj)
            else:
                 pre_obj = obj.__dict__.copy()
                 try:
                     for k, v in row.items():
                         setattr(obj, k, v)
                 except:
                     type_err, val_err, trcbk = sys.exc_info()
                     context['failure_count'] += 1
                     context['failures'].append({'error_type': type_err.__name__, 'error_value': val_err, 'name': row.get('name')})
                 else:
                    late_obj = obj.__dict__.copy()
                    pre_obj.pop('modify_date'), pre_obj.pop('create_date')
                    late_obj.pop('modify_date'), late_obj.pop('create_date')
                    s1 = set(map(str, pre_obj.values()))
                    s2 = set(map(str, late_obj.values()))
                    if s1 == s2:
                        context['noupdated'].append(obj)
                        continue
                    obj.save()
                    context['preupdated'].append(pre_obj)
                    context['updated'].append(late_obj)
    context['total_count'] = context['success_count'] + context['failure_count']
    fp.close()
    return context
