#!/usr/bin/env python
import json
import glob
import os
import argparse
from langdetect import detect


def get_lang(text):
    try:
        lang = detect(text)  # detecting language, return string language type (es,pt,fr,en, etc...).
    except:
        lang = "No detected"

    return lang



def validDoc(json_obj, min_title_length, min_abs_length, is_title_es ,is_abs_es):
    
    ti_es = json_obj["ti_es"]
    ab_es = json_obj["ab_es"]
    lang_ti = json_obj["lang_ti"]
    lang_ab = json_obj["lang_ab"]


    if (len(ti_es) < min_title_length or
        len(ab_es) < min_title_length or
        (is_title_es and lang_ti != "es")or
        (is_abs_es and lang_ab != "es")):

        return False


    return True

def get_title(information_obj):

    ti_es = information_obj.get("tituloPublico")
    information_obj.pop("tituloPublico",None)
    if  ti_es is None or not ti_es.strip(" ") or get_lang(ti_es) != 'es':
        ti_es = information_obj.get("tituloCientifico")

    if ti_es and get_lang(ti_es) == 'es':
        ti_es = ti_es.strip(" ")   
    else:
        ti_es ="" 

    return ti_es

def reec_to_mesinesp_format(obj,min_title_length, min_abs_Length, is_title_es,is_abs_es):
    _id = obj["identificador"]
    information_obj = obj["informacion"]

    title = get_title(information_obj)
    obj_to_send = {"_id":_id, "ti_es":title}

    information_obj.pop("tituloCientifico",None)
    information_obj.pop("tituloPublico",None)
    abstract = ""
    validValue = False
    for key, value in information_obj.items():
        if validValue:
            abstract = abstract + "\n\n"
            validValue = False
        if value and value.strip(" "):
            value = value.strip(" ")
            abstract = abstract + str(value)
            validValue = True


    lang_ab = get_lang(abstract)
    lang_ti = get_lang(abstract)


    obj_to_send.update({"ab_es": abstract,"lang_ab":lang_ab,"lang_ti":lang_ti })
    
    if  validDoc(obj_to_send, min_title_length, min_abs_Length, is_title_es,is_abs_es):
       return obj_to_send
    else:
        return None



def main(input_files, output_file_path, min_title_length, min_abs_Length, is_title_es,is_abs_es):
    # files=[os.path.abspath(file) for file in glob.glob(input_files_path)] 

    print("- Parsing and writing parsed records into the file -> ",output_file_path)

    oFile = open(output_file_path,'w')
    oFile.write('[')
    totalRecords = len(input_files)

    validDoc = False
    j = 0
    for i, file in enumerate(input_files):
        if validDoc:
            oFile.write(",\n")
            validDoc = False

        with open(file) as input_file:
            content = input_file.read()
            json_obj = json.loads(content)
            mesinesp_format = reec_to_mesinesp_format(json_obj,min_title_length, min_abs_Length, is_title_es,is_abs_es)

            if mesinesp_format:   
                json_obj = json.dumps(mesinesp_format,ensure_ascii=False)
                oFile.write(json_obj)
                validDoc = True
                j = j +1
            else:
                print("Ivalid Document:",i,file,"\n")
                pass
        print(i)

    oFile.write(']')
    oFile.close()

    print("\n- Done")
    print(f"- Total records: (Old - {totalRecords})\t (New - {j})")
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='reec_to_mesinesp_format.py',usage='%(prog)s [-i inputFolder.*json] [-o file.json]')

    parser.add_argument('-i','--input',metavar='', nargs="+", type=str,required=True, help ='Files to parse.') 
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for output file.')  
    parser.add_argument('-t','--minTitle',metavar='', type=str,default=10, help ='Minimum length for title. (Defaul = 10)') 
    parser.add_argument('-a','--minAbs',metavar='',type=int, default=100, help ='Minimum length for abstract.(Defaul = 100)')  
    parser.add_argument('--ti_es',action='store_true', help ='To get documents with title\'s language es.(Default = False)')
    parser.add_argument('--ab_es',action='store_true', help ='To get documents with abstract\'s language es.(Default = False)')  



    args = parser.parse_args()

    input_files = args.input
    output_file = args.output
    min_title_length = args.minTitle
    min_abs_Length = args.minAbs
    is_title_es = args.ti_es
    is_abs_es = args.ab_es


    current_dir = os.getcwd()
    output_path = os.path.join(current_dir,output_file)
   
    main(input_files,output_path,  min_title_length, min_abs_Length, is_title_es,is_abs_es)