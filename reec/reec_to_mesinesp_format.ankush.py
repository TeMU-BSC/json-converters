#!/usr/bin/env python
import json
import glob
import os
import argparse
from langdetect import detect


def get_lang(text):
    """It detect the language of text by langdetect.detect library. If the text is in more than one language, than it may detect wrong.

    :param text: Text tto detect language
    :type text: str
    :return: Language detected as (es, fr, en, etc..)
    :rtype: str
    """
    try:
        # detecting language, return string language type (es,pt,fr,en, etc...).
        lang = detect(text)
    except:
        lang = "No detected"

    return lang


def validDoc(json_obj, min_title_length, min_abs_length, is_title_es, is_abs_es):
    """This method is a validator of json object, by some criteris.
    It will check minmum length of title and abstract, passed by user.
    And also check if abstract and title is in spanish language, if user wants.

    :param json_obj: Object to valid.
    :type json_obj: dict
    :param min_title_length: minimum length for title, if the title length is less, it will retrun false.
    :type min_title_length: Int
    :param min_abs_length:  minimum length for abstract, if the title length is less, it will retrun false.
    :type min_abs_length: Int
    :param is_title_es: True, if title must be in Spanish, otherwise False.
    :type is_title_es: bool
    :param is_abs_es: True, if abstract must be in Spanish, otherwise False.
    :type is_abs_es: bool
    :return: True, if the object if valid, otherwise false.
    :rtype: bool

    """
    ti_es = json_obj["ti_es"]
    ab_es = json_obj["ab_es"]
    lang_ti = json_obj["lang_ti"]
    lang_ab = json_obj["lang_ab"]

    # False: If abstract is less than minimum abstract length, or title length is less than minimum title length,
    # or if title have to be in spanish but is not in spanish, or abstract have to be in spanish but isn't.
    if (len(ti_es) < min_title_length or
        len(ab_es) < min_title_length or
        (is_title_es and lang_ti != "es")or
            (is_abs_es and lang_ab != "es")):

        return False

    # If any of condition doesn't match than return true.
    return True


def get_title(information_obj):
    """Get title from infromaion object of REEC (Registro Español de Estudios Clínicos). It receives REEC's sub object information and retrun title from it.
    First it get public title and check the language, if the language isn't Spanish than go for scientific title,
    if the scientific title neather in Spanish, so the title will be empty.

    :param information_obj: Information object from REEC (Registro Español de Estudios Clínicos) document.
    :type information_obj: dict
    :return: Title , it may Spanish public or scientific title. If any of both is not in Spanish, than it will return a empty string.
    :rtype: str
    """

    # Public title
    ti_es = information_obj.get("tituloPublico")

    # If public title is null or is empty string, or is not in spanish, so go for scientific title.
    if ti_es is None or not ti_es.strip(" ") or get_lang(ti_es) != 'es':
        # Scientific title
        ti_es = information_obj.get("tituloCientifico")

    # If the title is not null and language is spanish, it will get title and strip it.
    if ti_es and get_lang(ti_es) == 'es':
        ti_es = ti_es.strip(" ")
    else:
        # Otherwise title will be a empty string.
        ti_es = ""

    return ti_es


def reec_to_mesinesp_format(obj, min_title_length, min_abs_Length, is_title_es, is_abs_es):
    """It converts REEC (Registro Español de Estudios Clínicos) to MESINESP (Medical Semantic Indexing in Spanish) format.
    It receives some extra parameter from user to valid the document, by his conditions

    :param obj: json Object (dict) to convert.
    :type json_obj: dict
    :param min_title_length: minimum length for title, if the title length is less, it will retrun false.
    :type min_title_length: Int
    :param min_abs_length:  minimum length for abstract, if the title length is less, it will retrun false.
    :type min_abs_length: Int
    :param is_title_es: True, if title must be in Spanish, otherwise False.
    :type is_title_es: bool
    :param is_abs_es: True, if abstract must be in Spanish, otherwise False.
    :type is_abs_es: bool
    :return: True, if the object if valid, otherwise false.
    :rtype: bool
    """

    _id = obj["identificador"]

    # information contains public title, scientific title and abstracts.
    information_obj = obj["informacion"]

    # Getting a valid title form information object
    title = get_title(information_obj)
    obj_to_send = {"_id": _id, "ti_es": title}

    # After getting title, must delete scientific and public title,
    # because it will get all other values as abstract and merge into one string.
    information_obj.pop("tituloCientifico", None)
    information_obj.pop("tituloPublico", None)

    abstract = ""
    validValue = False
    # Loop to get rest of the values (items) from information object and merge into one string with double break line in middle..
    for key, value in information_obj.items():
        if validValue:
            abstract = abstract + "\n\n"
            validValue = False
        if value and value.strip(" "):
            value = value.strip(" ")
            abstract = abstract + str(value)
            validValue = True

    # language.
    lang_ab = get_lang(abstract)
    lang_ti = get_lang(abstract)

    obj_to_send.update(
        {
            "ab_es": abstract,
            "lang_ab": lang_ab,
            "lang_ti": lang_ti
        })

    # If the document is not valid, it will return None 
    if validDoc(obj_to_send, min_title_length, min_abs_Length, is_title_es, is_abs_es):
        return obj_to_send
    else:
        return None


def main(input_files, output_file_path, min_title_length, min_abs_Length, is_title_es, is_abs_es):
    """Main function of script. It converts Reec (Registro Español de Estudios Clínicos) format data to MESINESP (Medical Semantic Indexing in Spanish) format.
    
    :param input_files: Input file's path to load REEC data. It can receive more than one file.
    :type input_files: List[string]
    :param output_file_path: Output file's path to dump new json MESINESP format
    :type output_file_path: str
    :param min_title_length: minimum length for title, if the title length is less, it will retrun false.
    :type min_title_length: Int
    :param min_abs_length:  minimum length for abstract, if the title length is less, it will retrun false.
    :type min_abs_length: Int
    :param is_title_es: True, if title must be in Spanish, otherwise False.
    :type is_title_es: bool
    :param is_abs_es: True, if abstract must be in Spanish, otherwise False.
    :type is_abs_es: bool
    :return: True, if the object if valid, otherwise false.
    :rtype: bool
    """

    # files=[os.path.abspath(file) for file in glob.glob(input_files_path)]

    print("- Parsing and writing parsed records into the file -> ", output_file_path)

    # Output file to dump json objects as list.
    oFile = open(output_file_path, 'w')

    # Staring with list opening.
    oFile.write('[')

    totalRecords = len(input_files)

    validDoc = False
    j = 0
    for i, file in enumerate(input_files):

        # If the document was valid, it will write a break line.
        if validDoc:
            oFile.write(",\n")
            validDoc = False

        with open(file) as input_file:
            content = input_file.read()
            json_obj = json.loads(content)
            
            # converting document from REEC format to MESINESP.
            mesinesp_format = reec_to_mesinesp_format(json_obj, min_title_length, min_abs_Length, is_title_es, is_abs_es)

            if mesinesp_format:
                json_obj = json.dumps(mesinesp_format, ensure_ascii=False)
                oFile.write(json_obj)
                validDoc = True
                j = j + 1
            else:
                print("\nInvalid Document:", i, file, "\n")
                pass
        print(i)

    oFile.write(']')
    oFile.close()

    print("\n- Done")
    print(f"- Total records: (Old - {totalRecords})\t (New - {j})")


if __name__ == '__main__':
    #argparse to get argument from terminal.
    parser = argparse.ArgumentParser(prog='reec_to_mesinesp_format.py', usage='%(prog)s [-i inputFolder.*json] [-o file.json]')

    parser.add_argument('-i', '--input', metavar='', nargs="+", type=str, required=True, help='Files to parse.')
    parser.add_argument('-o', '--output', metavar='', type=str, required=True, help='To define a name for output file.')
    parser.add_argument('-t', '--minTitle', metavar='', type=str, default=10, help='Minimum length for title. (Defaul = 10)')
    parser.add_argument('-a', '--minAbs', metavar='', type=int, default=100, help='Minimum length for abstract.(Defaul = 100)')
    parser.add_argument('--ti_es', action='store_true', help='To get documents with title\'s language es.(Default = False)')
    parser.add_argument('--ab_es', action='store_true', help='To get documents with abstract\'s language es.(Default = False)')

    args = parser.parse_args()

    # Getting all arguments required and passed b user
    input_files = args.input
    output_file = args.output
    min_title_length = args.minTitle
    min_abs_Length = args.minAbs
    is_title_es = args.ti_es
    is_abs_es = args.ab_es

    current_dir = os.getcwd()
    output_path = os.path.join(current_dir, output_file)

    main(input_files, output_path,  min_title_length,min_abs_Length, is_title_es, is_abs_es)
