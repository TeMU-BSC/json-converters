#!/usr/bin/env python
import json
import glob
import os
import argparse
from langdetect import detect



def getLang(text):
    try:
        lang = detect(text)  # detecting language, return string language type (es,pt,fr,en, etc...).
    except:
        lang = "No detected"

    return lang

def reecToMesinespFormat(obj):
    _id = obj["identificador"]
    informationObj = obj["informacion"]

    ti_es = informationObj.get("tituloPublico")
    informationObj.pop("tituloPublico",None)
    if  ti_es is None or not ti_es.strip(" ") or getLang(ti_es) != 'es':
        ti_es = informationObj.get("tituloCientifico")

    if ti_es and getLang(ti_es) == 'es':
        ti_es = ti_es.strip(" ")   
    else:
        ti_es ="" 
    informationObj.pop("tituloCientifico",None)

    objToSend = {"_id":_id, "ti_es":ti_es}
    
    stringObj = ""
    i = 0
    for key, value in informationObj.items():
        if i > 0:
            stringObj = stringObj + "\n\n"
        if value:
            value = value.strip(" ")
            stringObj = stringObj + str(value)
        i = i+1

    lang = getLang(stringObj)
    objToSend.update({"ab_es": stringObj,"lang":lang})

    return objToSend

def main(input_files_path, output_file_path):
    # files=[os.path.abspath(file) for file in glob.glob(input_files_path)] 


    if not input_files_path:
        print("Error:", input_files_path, "No files found,  Please  check the argument.")
        return -1
    

    outputFile = open(output_file_path,'w')
    outputFile.write('[')
    validDocs = 0
    i = 0
    for file in input_files_path:
        with open(file) as input_file:
            content = input_file.read()
            jsonObj = json.loads(content)
            mesinespFormat = reecToMesinespFormat(jsonObj)

            if mesinespFormat:
                if validDocs > 0:
                    outputFile.write(',\n')    
                data_json = json.dumps(mesinespFormat,ensure_ascii=False)
                outputFile.write(data_json)

                validDocs = validDocs + 1
            else:
                # print("Error:",i,file,"Object empty\n")
                pass
        print(i)
        i = i + 1

    outputFile.write(']')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='reec_to_mesinesp_format.py',usage='%(prog)s [-i inputFolder.*json] [-o file.json]')

    parser.add_argument('-i','--input',metavar='', nargs='+', type=str,required=True, help ='To define a name for input file/s.') 
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for output file.')  

    args = parser.parse_args()

    input_files = args.input
    output_file = args.output
    
    current_dir = os.getcwd()
    output_path = os.path.join(current_dir,output_file)


    main(input_files,output_path)