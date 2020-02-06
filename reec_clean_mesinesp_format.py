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



def validDoc(jsonObj, minTitleLength, minAbsLenth, isTitleEs ,isAbsEs):
    
    ti_es = jsonObj["ti_es"]
    ab_es = jsonObj["ab_es"]
    lang_ti = jsonObj["lang_ti"]
    lang_ab = jsonObj["lang_ab"]


    if (len(ti_es) < minTitleLength or
        len(ab_es) < minTitleLength or
        (isTitleEs and lang_ti != "es")or
        (isAbsEs and lang_ab != "es")):

        return False


    return True

def get_title(informationObj):

    ti_es = informationObj.get("tituloPublico")
    informationObj.pop("tituloPublico",None)
    if  ti_es is None or not ti_es.strip(" ") or getLang(ti_es) != 'es':
        ti_es = informationObj.get("tituloCientifico")

    if ti_es and getLang(ti_es) == 'es':
        ti_es = ti_es.strip(" ")   
    else:
        ti_es ="" 

    return ti_es

def reecToMesinespFormat(obj,minTitleLength, minAbsLenth, isTitleEs,isAbsEs):
    _id = obj["identificador"]
    informationObj = obj["informacion"]

    title = get_title(informationObj)
    objToSend = {"_id":_id, "ti_es":title}

    informationObj.pop("tituloCientifico",None)
    informationObj.pop("tituloPublico",None)
    abstract = ""
    validValue = False
    for key, value in informationObj.items():
        if validValue:
            abstract = abstract + "\n\n"
            validValue = False
        if value :
            value = value.strip(" ")
            abstract = abstract + str(value)
            validValue = True


    lang_ab = getLang(abstract)
    lang_ti = getLang(abstract)


    objToSend.update({"ab_es": abstract,"lang_ab":lang_ab,"lang_ti":lang_ti })
    
    if  validDoc(objToSend, minTitleLength, minAbsLenth, isTitleEs,isAbsEs):
       return objToSend
    else:
        return None



def main(input_files, output_file_path, minTitleLength, minAbsLenth, isTitleEs,isAbsEs=False):
    # files=[os.path.abspath(file) for file in glob.glob(input_files_path)] 

    print("- Parsing and writing parsed records into the file -> ",output_file_path)

    oFile = open(output_file_path,'w')
    oFile.write('[')
    totalRecords = len(input_files)

    validDoc = False
    j = 0;
    for i, file in enumerate(input_files):
        if validDoc:
            oFile.write(",\n")
            validDoc = False

        with open(file) as input_file:
            content = input_file.read()
            jsonObj = json.loads(content)
            mesinespFormat = reecToMesinespFormat(jsonObj,minTitleLength, minAbsLenth, isTitleEs,isAbsEs)

            if mesinespFormat:   
                jsonObj = json.dumps(mesinespFormat,ensure_ascii=False)
                oFile.write(jsonObj)
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
    parser.add_argument('--titleEs',metavar='',type=bool, default=True, help ='To get documents with language es.(Default = False)')  


    args = parser.parse_args()

    input_files = args.input
    output_file = args.output
    minTitleLength = args.minTitle
    minAbsLenth = args.minAbs
    isTitleEs = args.titleEs

    current_dir = os.getcwd()
    output_path = os.path.join(current_dir,output_file)
   
    
    main(input_files,output_path,  minTitleLength, minAbsLenth, isTitleEs)