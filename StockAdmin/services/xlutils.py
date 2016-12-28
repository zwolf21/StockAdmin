import os
import pandas
from django.http import HttpResponse, StreamingHttpResponse

def excel_response(queryset, response_file_name='backup.xlsx', index=False):

    if type(queryset) == list:
        records = queryset
    else:
        records = queryset.values()
  
    pd = pandas.DataFrame.from_records(records)
    pd.to_excel('backup.xlsx', index=index)
    fp = open('backup.xlsx', 'rb')
    response = StreamingHttpResponse(fp, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename='+response_file_name
    # os.unlink(response_file_name)
    return response
