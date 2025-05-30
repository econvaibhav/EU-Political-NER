"""Prepare platform-specific text documents from a CSV or XLSX export of research notes.

Defaults reproduce the surviving notebook's column mapping. Input text and
original identifiers are preserved; output is CSV, with no external requests.
"""
import argparse
import csv
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from political_ner.matching import COUNTRY_CODES

IDENTIFIER_COLUMN='Your identifier (e.g. PT1, FR3, BG2)\n'
PLATFORM_COLUMNS={
    'tiktok':'Please list the names of official or affiliated accounts where you have seen these people or parties:\n',
    'instagram':'Please list the names of official or affiliated accounts where you have seen these people or parties:',
}
CORRECTIONS={'DE§':'DE3','BG4':'BG3','F13':'FI3','HRO':'HR2','HRS':'HR2','HU0':'HU3'}


def prepare(rows):
    result=[]
    seen=set()
    for row in rows:
        original=row[IDENTIFIER_COLUMN]
        cleaned=''.join(original.split()).upper()
        identifier=CORRECTIONS.get(cleaned,cleaned)
        country=COUNTRY_CODES.get(identifier[:2],'Unknown')
        if not row['ID'].strip():
            raise ValueError('Every row needs an ID')
        for platform,col in PLATFORM_COLUMNS.items():
            text=row[col]
            if not text.strip():
                continue
            document_id=f'{row["ID"]}:{platform}'
            if document_id in seen:
                raise ValueError(f'Duplicate document_id: {document_id}')
            seen.add(document_id)
            result.append({'document_id':document_id,'platform':platform,'text':text,
                           'source_country':country,'original_identifier':original,
                           'corrected_identifier':identifier})
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():
        p.error('Output exists. Choose a new path.')
    needed={'ID',IDENTIFIER_COLUMN,*PLATFORM_COLUMNS.values()}
    if a.input.suffix.lower() == '.xlsx':
        from openpyxl import load_workbook
        book=load_workbook(a.input,read_only=True,data_only=True)
        sheet=book.active
        sheet.reset_dimensions()  # The supplied export incorrectly reports A1:A1.
        values=iter(sheet.values)
        headers=next(values)
        rows=[dict(zip(headers,('' if v is None else str(v) for v in row))) for row in values]
        book.close()
    else:
        with a.input.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            headers=reader.fieldnames or []
            rows=list(reader)
    if not needed<=set(headers):
        p.error('Column labels differ from the supplied export. Check PLATFORM_COLUMNS.')
    result=prepare(rows)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['document_id','platform','text','source_country',
                                      'original_identifier','corrected_identifier'])
        w.writeheader();w.writerows(result)
    print(f'Prepared {len(result)} nonempty platform documents.')

