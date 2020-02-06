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

import click


@click.command()
@click.argument('input', type=click.File('r'), nargs=-1)
@click.argument('output', type=click.Path(exists=True), nargs=1)
@click.option('--lang', help='Language to filter (es, en, ...).')
# @click.option('--lang', nargs=-1, help='Language(s) to filter (es, en, ...).')
@click.option('--encoding', default='utf-8', help='Encoding format.')
@click.option('--ensure-ascii', default=False, help='Force to write only ASCII characters (i.e. no graphical accents allowed).')
@click.option('--separators', default=(',', ':'), help='Encoding format.')
def read_and_write_files(input, output, lang, encoding, ensure_ascii, separators):
    '''Convert from patent's json schema to mesinesp's json schema.'''
    for file in input:
        # Each line of the .gz compressed file is a patent
        with gzip.open(file.name, 'r') as f:
            content = f.readlines()
        patents = [json.loads(line) for line in content]
        for patent in patents:
            # Only one language accepted
            title = [patent.get('title_localized').get('text') for patent in patent.get('title_localized') if title.get('language') == lang]
            abstract = [patent.get('abstract_localized').get('text') for patent in patent.get('abstract_localized') if title.get('language') == lang]

            # TODO many languages accepted
            # has_lang_title = all([True for title in patent.get('title_localized') if title.get('language') in lang])
            # has_lang_abstract = all([True for title in patent.get('abstract_localized') if title.get('language') in lang])
            # has_desired_lang = has_desired_lang and has_lang_abstract

        with open(os.path.join(dst, ntpath.basename(file.name)), 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=ensure_ascii,
                      separators=separators)


def convert_patent_to_mesinesp()

if __name__ == '__main__':
    minify()
