'''
Filter patents in JSON (that are compressed in GZ format files) by 'es' Spanish ISO code.

Usage:
$ python filter_patents.py --infiles *.gz --outfile patents_es.multilinejson

Author: https://github.com/aasensios
'''

import argparse
import gzip
import html
import json
import ntpath
import os
import sys
from typing import List


def main():
    '''Read some gz compressed files. Each line of the uncompresseed file is a JSON object representing a patent.
    Filter only the patents with title and abstract in Spanish language ('es' ISO code).
    Convert from original patent's json schema to mesinesp's json schema, in addition of IPC codes and publication date.
    Write each filtered and converted JSON object in a new line (multilinejson format) to later easily import them into MongoDB.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('--infiles', nargs='*', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    patents_in_spanish = list()

    for i, file in enumerate(args.infiles, start=1):
        print(f'Processing {file.name} ({i} of {len(args.infiles)})...')

        filename = ntpath.basename(file.name)
        extension = os.path.splitext(file.name)[1]

        if extension != '.gz':
            return 'The input files must be GZ compressed files.'
        
        with gzip.open(filename, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            patent = json.loads(line)

            ti_es = [title.get('text') for title in patent.get('title_localized') if title.get('language') == 'es']
            ab_es = [abstract.get('text') for abstract in patent.get('abstract_localized') if abstract.get('language') == 'es']
            ipc_codes = [ipc.get('code') for ipc in patent.get('ipc')]

            if ti_es and ab_es:
                mesinesp_format = {
                    '_id': patent.get('publication_number'),
                    'ti_es': html.unescape(ti_es[0]),
                    'ab_es': html.unescape(ab_es[0]),
                    'ipc_codes': ipc_codes,
                    'publication_date': patent.get('publication_date'),
                }
                patents_in_spanish.append(mesinesp_format)

    with open(args.outfile.name, 'w') as f:
        for patent in patents_in_spanish:
            json.dump(patent, f, ensure_ascii=False)
            f.write('\n')


if __name__ == '__main__':
    main()
