from io import BytesIO
import xlsxwriter

def excel_response(records):
    output = BytesIO()
    wb = xlsxwriter.Workbook(output, {'inmemory': True, 'remove_timezone': True})
    ws = wb.add_worksheet()
    hdr = records[0].keys()
    ws.write_row(0,0, hdr)
    for i, row in enumerate(records):
        ws.write_row(i+1, 0, map(str, row.values()))
    wb.close()
    return output.getvalue()
