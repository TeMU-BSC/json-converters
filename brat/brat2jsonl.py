'''
Convert brat annotated texts (txt + ann pairs of files) into a json file.

Author: https://github.com/aasensios

Motivation:
https://support.prodi.gy/t/importing-existing-custom-annotated-data-from-brat/821

Usage:
$ python3 brat2jsonl.py --txtfiles data/*.txt --annfiles data/*.ann --outfile data.jsonl

Example:

Input (data/ directory):
123.utf8.txt
123.utf8.ann
456.utf8.txt
456.utf8.ann
789.utf8.txt
789.utf8.ann

Output (data.jsonl):
{"text":"Apple updates its analytics service with new metrics","spans":[{"start":0,"end":5,"label":"ORG","note":"Tech company"}]}
{"text":"Google updates its analytics service with new metrics","spans":[{"start":0,"end":6,"label":"ORG","note":"Tech company"}]}
{"text":"Facebook updates its analytics service with new metrics","spans":[{"start":0,"end":8,"label":"ORG","note":"Tech company"}]}
'''

import argparse
import csv
import json
import sys
import tokenize

# Testing built-in python tokenizer 
# with tokenize.open('small.txt') as f:
#     tokens = tokenize.generate_tokens(f.read)
#     for token in tokens:
#         print(token)

def brat_to_prodigy(txt_file, ann_file) -> dict:
    meta = dict(file=txt_file)
    text = str()
    spans = list()
    tokens = list()

    with open(txt_file) as textfile:
        text = textfile.read()

    # Throws a tokenize error on some txt files, such as '321108781.utf8.txt'
    # with tokenize.open(txt_file) as f:
    #     python_tokens = tokenize.generate_tokens(f.read)
    #     tokens = [dict(text=token.string, start=token.start[1], end=token.end[1], id=i) for i, token in enumerate(python_tokens)]

    with open(ann_file) as tsvfile:
        note_rows, annotation_rows = list(), list()
        for row in tsvfile:
            note_rows.append(row) if row.startswith('#') else annotation_rows.append(row)
        notes = list(csv.DictReader(note_rows, fieldnames=['note_id', 'middle_section', 'note'], dialect=csv.excel_tab))
        annotations = list(csv.DictReader(annotation_rows, fieldnames=['ann_id', 'middle_section', 'evidence'], dialect=csv.excel_tab))

    spans = list()
    for ann in annotations:
        middle = ann['middle_section'].split(' ')
        note = next((note['note'] for note in notes if note['middle_section'].split(' ')[1] == ann['ann_id']), None)
        span = dict(start=int(middle[1]), end=int(middle[2]), label=middle[0], note=note)
        spans.append(span)

    prodigy_format = dict(meta=meta, text=text, spans=spans, tokens=tokens)
    return prodigy_format


def main():
    '''Read some txt and ann pairs of files.
    Each txt file should have its corresponding ann file.
    Convert from brat format (ann as tsv) into multiline json format (jsonl).
    See https://jsonlines.org/.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--txtfiles', nargs='*', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--annfiles', nargs='*', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    pairs = list(zip(args.txtfiles, args.annfiles))
    annotations = [brat_to_prodigy(txt.name, ann.name) for (txt, ann) in pairs]

    with open(args.outfile.name, 'a') as jsonlfile:
        for annotation in annotations:
            json.dump(annotation, jsonlfile, ensure_ascii=False, separators=[',', ':'])
            jsonlfile.write('\n')


if __name__ == '__main__':
    main()
