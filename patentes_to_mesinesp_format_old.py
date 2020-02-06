'''
Script that converts from PATENTS json schema to MESINESP json schema.

Author: https://github.com/mmaguero
Based on reec_to_mesinesp_format.py, adapted for patents.

Code partially formatted by: https://github.com/aasensios

TODO: avoid hardcoded literals such as "es"
TODO: avoid deep nesting code blocks
TODO: replace input type: file list (as a glob) is better than a directory
'''

import json
import glob
import os
import argparse
import gzip
from langdetect import detect
from tempfile import mkstemp
from shutil import move
from os import fdopen


def get_lang(text):
    try:
        # Return string language code (es, pt, fr, en...)
        lang = detect(text)
    except:
        lang = "No detected"
    return lang


def patents_to_mesinesp_format(obj):
    objToSend = dict()
    _id = obj.get("publication_number", None)  # ["publication_number"]
    titleObj = obj.get("title_localized", None)  # ["title_localized"]
    abstractObj = obj.get("abstract_localized", None)  # ["abstract_localized"]
    if _id and titleObj and abstractObj:
        ti_es = ""
        for to in titleObj:
            ti_es = to.get("text")
            to.pop("text")
            ti_es_l = to.get("language")
            to.pop("language")
            if ti_es and ti_es.strip(" ") and (ti_es_l == 'es'):
                ti_es = ti_es.strip(" ")
                break
            else:
                ti_es = ""
        ab_es = ""
        ab_es_l = ""
        for ao in abstractObj:
            ab_es = ao.get("text", None)
            ao.pop("text", None)
            ab_es_l = ao.get("language", None)
            ao.pop("language", None)
            if ab_es and ab_es.strip(" ") and (ab_es_l == 'es'):
                ab_es = ab_es.strip(" ")
                break
            else:
                ab_es = ""
        objToSend = {"_id": _id, "ti_es": ti_es, "ab_es": ab_es, "lang": ab_es_l}
        print(objToSend)
    return objToSend


def main(input_files_path, output_file_path):
    # files = [os.path.abspath(file) for file in glob.glob(input_files_path)]
    if not input_files_path:
        print("Error:", input_files_path, "No files found,  Please check the argument.")
        return -1
    i = 0  # count files
    path = input_files_path[0]
    all_files = glob.glob(path + "/*.gz")
    for file in all_files:
        fh, abs_path = mkstemp()
        with fdopen(fh, 'w') as outputFile:
            # outputFile = open(output_file_path,'w')
            with gzip.open(file, 'rb') as input_file:
                outputFile.write('[')
                validDocs = 0  # count objects
                # content = input_file.read()
                for content in input_file:
                    jsonObj = json.loads(content)
                    mesinespFormatObj = patents_to_mesinesp_format(jsonObj)
                    mesinespFormat = mesinespFormatObj if (mesinespFormatObj.get("ti_es") != '' or mesinespFormatObj.get("ab_es") != '') else None
                    if mesinespFormat:
                        if validDocs > 0:
                            outputFile.write(',\n')
                        data_json = json.dumps(mesinespFormat, ensure_ascii=False)
                        outputFile.write(data_json)

                        validDocs = validDocs + 1
                    else:
                        # print("Error:",i,file,"Object empty\n")
                        pass
                outputFile.write(']')
            input_file.close()
        print()
        print("Number: {}, File: {}".format(i, os.path.basename(input_file.name)))
        print()
        i = i + 1
        try:
            move(abs_path, output_file_path+'/'+os.path.basename(input_file.name)+'.json')
        except Exception as e:
            print(e)
            os.makedirs(output_file_path, exist_ok=True)
            move(abs_path, os.path.join(output_file_path, os.path.basename(input_file.name)+'.json'))
        outputFile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='patentes_to_mesinesp_format.py', usage='%(prog)s [-i inputFolder.*json] [-o file.json]')

    parser.add_argument('-i', '--input', metavar='', nargs='+', type=str, required=True, help='To define a name for input file.')
    parser.add_argument('-o', '--output', metavar='', type=str, required=True, help='To define a name for output file.')

    args = parser.parse_args()

    input_files = args.input
    output_file = args.output

    current_dir = os.getcwd()
    output_path = os.path.join(current_dir, output_file)

    main(input_files, output_path)
