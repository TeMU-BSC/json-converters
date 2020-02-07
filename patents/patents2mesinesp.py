'''
Script that converts from PATENTS json schema to MESINESP json schema.

Author: https://github.com/aasensios

TODO: avoid hardcoded literals such as "es"
TODO: avoid deep nesting code blocks
TODO: replace input type: file list (as a glob) is better than a directory
'''

import gzip
import json
import ntpath
import os
from typing import List, Tuple

import click


@click.command()
@click.argument('input-files', type=click.File('r'), nargs=-1)
@click.argument('output-dir', type=click.Path(exists=True))
# @click.option('--src-keys', multiple=True, help='List of source keys.')
# @click.option('--dst-keys', multiple=True, help='List of destination keys.')
@click.option('--lang', multiple=True,
              help='Language two-letter codes to filter, for example: es en.')
@click.option('--encoding', default='utf-8', help='Encoding format.')
@click.option('--ensure-ascii', default=False, help='Force writing only ASCII \
              characters, for exmaple, no graphical accents allowed.')
@click.option('--separators', default=(',', ':'), help='Encoding format.')
def read_gz_and_write_json(input_files, output_dir,
                           # src_keys, dst_keys,
                           lang, encoding, ensure_ascii, separators):
    '''Read some gz files, for each file convert its content from patent's
    json schema to mesinesp's json schema, and finally write a patent per
    line into a txt file with the same filename as its corresponding gz file.
    '''
    # Get the keys mappings
    # keys_mappings = list(zip(src_keys, dst_keys))

    for i, file in enumerate(input_files, start=1):
        filename = ntpath.basename(file.name)
        extension = os.path.splitext(file.name)[1]

        # Check if the input file is GZ compressed.
        # Each line of the input file is a patent.
        if extension == '.gz':
            with gzip.open(file.name, 'r') as f:
                content = f.readlines()
        else:
            with open(file.name, 'r') as f:
                content = f.readlines()
        patents = [json.loads(line) for line in content]

        # Python3.8 Assignment Expression (Walrus operator ':=') to avoid
        # calling the function twice.
        mesinesps = [mesinesp for patent in patents
                     if (mesinesp := convert_patent_to_mesinesp(patent, lang))]

        # Write to output file
        output_filename = filename.replace(extension, '.txt')
        with open(os.path.join(output_dir, output_filename), 'w', encoding=encoding) as f:
            json.dump(mesinesps, f, ensure_ascii=ensure_ascii, separators=separators)

        # Feedback for terminal
        print(filename, f'[ {i} of {len(input_files)} ]')


def convert_patent_to_mesinesp(patent: dict, lang: tuple) -> dict:
    '''Convert patent json schema to mesinesp json schema.'''
    mesinesp = dict()

    ti_es = [title.get('text') for title in patent.get('title_localized')
            if title.get('language') in lang]
    ab_es = [abstract.get('text') for abstract in patent.get('abstract_localized')
            if abstract.get('language') in lang]
    if ti_es and ab_es:
        mesinesp = {
            '_id': patent.get('publication_number'),
            'ti_es': ti_es[0],
            'ab_es': ab_es[0]
        }

    # for src_key, dst_key in keys_mappings:
    #     value = str()
    #     if type(patent.get(src_key)) == 'str':
    #         value = patent.get(dst_key)
    #     elif type(patent.get(src_key)) == 'list':
    #         value = [item.get('text') for item in patent.get(src_key)
    #                  if key.get('language') in lang]
    #     mesinesp[dst_key] = value

    return mesinesp


if __name__ == '__main__':
    read_gz_and_write_json()
