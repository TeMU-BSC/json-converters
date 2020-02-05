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


def validDoc(jsonObj, minTitleLength, minAbsLenth, isTitleEs):

    ti_es = jsonObj["ti_es"]
    ab_es = jsonObj["ab_es"]
    lang_ti = jsonObj["lang"]

    if (len(ti_es) < minTitleLength or
        len(ab_es) < minTitleLength or
        (isTitleEs and lang_ti != "es")):

        return False


    return True




def main(input_path,ouput_path, minTitleLength, minAbsLenth, isTitleEs):

    
  
    newObjsList = []
    totalRecords = None
    with open(input_path) as file:
        print("- Parsing all documents")
        content = file.read()
        listJsonObj = json.loads(content)
        totalRecords = len(listJsonObj)
        newObjsList = [jsonObj for jsonObj in listJsonObj if validDoc(jsonObj, minTitleLength, minAbsLenth, isTitleEs) ]


    oFile = open(ouput_path,'w')
    oFile.write('[')
    print("\n- Writing parsed records into the file", ouput_path)
    for i, obj in enumerate(newObjsList):
        jsonObj = json.dumps(obj,ensure_ascii=False)
        oFile.write(jsonObj)
        oFile.write(",\n")

    oFile.write(']')
    oFile.close()

    print("\n- Done")
    print(f"- Total records: (Old - {totalRecords})\t (New - {len(newObjsList)})")
 



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='reec_to_mesinesp_format.py',usage='%(prog)s [-i inputFolder.*json] [-o file.json]')

    parser.add_argument('-i','--input',metavar='', type=str,required=True, help ='To define a name for input file.') 
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for output file.')  
    parser.add_argument('-t','--minTitle',metavar='', type=str,default=10, help ='Minimum length for title. (Defaul = 10)') 
    parser.add_argument('-a','--minAbs',metavar='',type=int, default=100, help ='Minimum length for abstract.(Defaul = 100)')  
    parser.add_argument('--titleEs',metavar='',type=bool, default=True, help ='To get documents with language es.(Default = False)')  


    args = parser.parse_args()

    input_files = args.input
    output_file = args.output
    minTitleLength = args.minTitle
    minAbsLenth = args.minAbs
    isTitleEs = args.titleEs

    current_dir = os.getcwd()
    input_path = os.path.join(current_dir,input_files)
    output_path = os.path.join(current_dir,output_file)


    
    
    main(input_path,output_path,  minTitleLength, minAbsLenth, isTitleEs)