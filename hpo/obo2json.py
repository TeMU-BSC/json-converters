'''
Script that converts from Human Phenotype Ontology (HPO) OBO format to its
equivalent JSON format.

HPO webpage: https://hpo.jax.org/
Python OBO format parser: https://pypi.org/project/pronto/

Author: https://github.com/aasensios
'''

import json

import pronto
import click


@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output')
def read_obo_and_write_json(input, output):
    '''Read an OBO file and writes its conversion into a JSON file.'''
    hpo = pronto.Ontology(input.name)
    hp_dict_list = [convert_term_to_dict(term) for term in hpo.terms()]
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(hp_dict_list, f, ensure_ascii=False)


def convert_term_to_dict(term: pronto.Term) -> dict:
    '''Convert OBO format into JSON format.
    https://owlcollab.github.io/oboformat/doc/GO.format.obo-1_2.html
    https://pronto.readthedocs.io/en/latest/_modules/pronto/synonym.html#Synonym
    https://pronto.readthedocs.io/en/latest/_modules/pronto/xref.html#Xref
    '''
    return {
        'id': term.id,
        'name': term.name,
        'definition': term.definition,
        'synonyms': [synonym.description for synonym in term.synonyms],
        'xrefs': [xref.id for xref in term.xrefs],
        'comment': term.comment,
        'isLeaf': term.is_leaf(),
    }


if __name__ == '__main__':
    read_obo_and_write_json()
