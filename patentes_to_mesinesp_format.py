#!/usr/bin/env python
import json
import glob
import os
import argparse
from langdetect import detect
import gzip
from tempfile import mkstemp
from shutil import move
from os import fdopen

'''
based on reec_to_mesinesp_format.py for patents
'''


def getLang(text):
    try:
        lang = detect(text)  # detecting language, return string language type (es,pt,fr,en, etc...).
    except:
        lang = "No detected"

    return lang


def patentesToMesinespFormat(obj):
    _id = obj["publication_number"]
    titleObj = obj["title_localized"]
    abstractObj = obj["abstract_localized"]

    ti_es = ""
    for to in titleObj:
        
        ti_es = to.get("text")
        to.pop("text",None)
        ti_es_l = to.get("language")
        to.pop("language",None)
        '''if  ti_es is None or not ti_es.strip(" ") or getLang(ti_es) != 'es' or ti_es_l != 'es':
            ti_es = ""#informationObj.get("tituloCientifico")'''

        ti_lang = getLang(ti_es)
        if ti_es and ti_es.strip(" ") and (ti_lang == 'es' or ti_es_l == 'es'):
            ti_es = ti_es.strip(" ")
            break;   
        else:
            ti_es ="" 
        #informationObj.pop("tituloCientifico",None)
    
    ab_es = ""    
    for ao in abstractObj:
        
        ab_es = ao.get("text")
        ao.pop("text",None)
        ab_es_l = to.get("language")
        ao.pop("language",None)
        '''if  ab_es is None or not ab_es.strip(" ") or getLang(ab_es) != 'es' or ab_es_l != 'es':
            ab_es = ""#informationObj.get("tituloCientifico")'''
        
        ab_lang = getLang(ab_es)
        if ab_es and ab_es.strip(" ") and (ab_lang == 'es' or ab_es_l == 'es'):
            ab_es = ab_es.strip(" ")  
            break; 
        else:
            ab_es ="" 
        #informationObj.pop("tituloCientifico",None)

    lang = getLang(ab_es) if len(ab_es)>0 else ''
    objToSend = {"_id":_id, "ti_es":ti_es, "ab_es":ab_es, "lang":lang}
    print(objToSend)
    
    '''stringObj = ""
    i = 0
    for key, value in abstractObj.items():
        if i > 0:
            stringObj = stringObj + "\n\n"
        if value:
            value = value.strip(" ")
            stringObj = stringObj + str(value)
        i = i+1

    lang = getLang(stringObj)
    objToSend.update({"ab_es": stringObj,"lang":lang})'''

    return objToSend


def main(input_files_path, output_file_path):
    #files=[os.path.abspath(file) for file in glob.glob(input_files_path)] 

    if not input_files_path:
        print("Error:", input_files_path, "No files found,  Please  check the argument.")
        return -1
    
    i = 0 #count files
    path = input_files_path[0]
    all_files = glob.glob(path + "/*.gz")
    for file in all_files:
        fh, abs_path = mkstemp()
        with fdopen(fh,'w') as outputFile:
            #outputFile = open(output_file_path,'w')
            with gzip.open(file, 'rb') as input_file:
                outputFile.write('[')
                validDocs = 0 #count objects
                #content = input_file.read()
                for content in input_file:
                    jsonObj = json.loads(content)
                    mesinespFormatObj = patentesToMesinespFormat(jsonObj)
                    mesinespFormat = mesinespFormatObj if (mesinespFormatObj.get("ti_es") != '' or mesinespFormatObj.get("lang") == 'es') else None
    
                    if mesinespFormat:
                        if validDocs > 0:
                            outputFile.write(',\n')    
                        data_json = json.dumps(mesinespFormat,ensure_ascii=False)
                        outputFile.write(data_json)

                        validDocs = validDocs + 1
                    else:
                        # print("Error:",i,file,"Object empty\n")
                        pass
                
                outputFile.write(']')
            
            input_file.close()
        
        print()
        print("Number: {}, File: {}".format(i,os.path.basename(input_file.name)))
        print()
        i = i + 1
        
        try:
            move(abs_path, output_file_path+'/'+os.path.basename(input_file.name)+'.json')
        except Exception as e:
            print(e)
            os.makedirs(output_file_path, exist_ok=True)
            move(abs_path, output_file_path+'/'+os.path.basename(input_file.name)+'.json')
            
        outputFile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog ='patentes_to_mesinesp_format.py',usage='%(prog)s [-i inputFolder.*json] [-o file.json]')

    parser.add_argument('-i','--input',metavar='', nargs='+', type=str,required=True, help ='To define a name for input file.') 
    parser.add_argument('-o','--output',metavar='',type=str,required=True, help ='To define a name for output file.')  

    args = parser.parse_args()

    input_files = args.input
    output_file = args.output
    
    current_dir = os.getcwd()
    output_path = os.path.join(current_dir,output_file)


    main(input_files,output_path)
