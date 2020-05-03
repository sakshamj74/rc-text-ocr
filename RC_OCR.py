import boto3
import csv
import re
import pandas as pd
import os
from xlsxwriter import Workbook
with open('credentials.csv','r') as input:
    next(input)
    reader=csv.reader(input)
    for line in reader:
        access_key_id=line[2]
        secret_access_key=line[3]
client=boto3.client('rekognition',aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key)
path='/home/sak/DL/material/text_ocr/RC/RC'
final_path=os.listdir('/home/sak/DL/material/text_ocr/RC/RC')
final_data=[]  # A list to store extracted information
for file in final_path[:3]:
    photo = os.path.join(path,file)
    print("Under Process:-",file)
    with open(photo,'rb') as source_image:
        source_bytes=source_image.read()
    response=client.detect_text(Image={'Bytes':source_bytes})
    temp=[]
    for k in response['TextDetections']:
        temp.append(k['DetectedText'])
    #print(temp)
    dicc={"Registration_no":"Not Found","Engine_no":"Not Found","Chasis_no":"Not Found","Register_date":"Not Found","Name":"Not Found"}
    for i in temp:
        field=i
        #######  Finding Registration Number   ###########
        if re.findall(r'\b([A-Z]{2}[0-9A-Z]{4}[0-9]{4})\b',i):
            dicc['Registration_no']=re.findall(r'\b([A-Z]{2}[0-9A-Z]{4}[0-9]{4})\b',i)[0]
            continue
        elif re.findall(r'\b([A-Z]{2}[0-9A-Z]{3}[\s][0-9]{4})\b',i):
            dicc['Registration_no']=re.findall(r'\b([A-Z]{2}[0-9A-Z]{3}[\s][0-9]{4})\b',i)[0]
            continue
        elif re.findall(r'\b([A-Z]{2}[0-9A-Z]{2}[-][A-Z]{1}[-][0-9]{4})\b',i):
            dicc['Registration_no']=re.findall(r'\b([A-Z]{2}[0-9A-Z]{2}[-][A-Z]{1}[-][0-9]{4})\b',i)[0]
            continue 
        elif re.search('REGN . NO',i) or re.search("Registration",i) is not None:
            reg_no=re.search("[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}$",i)
            if reg_no is not None:
                reg_no = i[reg_no.start(): reg_no.end()]
                dicc['Registration_no']=reg_no
            continue
         
                
    
        ###### CHASIS NO  ##########
        # TRY:1 
        elif (re.search('CH', i)  or re.search('CH. NO',i)) is not None: 
            chasis=re.search("[a-zA-Z]{1,3}[0-9][a-zA-Z]{1,4}.*[0-9]{6,8}",i)
            if chasis is not None:
                chasis = i[chasis.start():chasis.end()]
                dicc['Chasis_no']=re.findall(r'[a-zA-Z]{1,3}[0-9][a-zA-Z]{1,4}.*[0-9]{6,8}',i)[0]
            continue
        # TRY:2
        elif re.findall(r'\b([A-Z0-9]{14,})\b',i):
            dicc['Chasis_no']=re.findall(r'\b([A-Z0-9]{14,})\b',i)[0]
            continue
        # TRY:3
        elif re.findall(r'[a-zA-Z]{1,3}[0-9][a-zA-Z]{1,4}.*[0-9]{6,8}',i):
            dicc['Chasis_no']=re.findall(r'[a-zA-Z]{1,3}[0-9][a-zA-Z]{1,4}.*[0-9]{6,8}',i)[0]
            continue
            
            
        ######  Engine Number   ############
        elif re.findall('[a-zA-Z]{1,3}[0-9].*[0-9]{3,6}',i) :
            dicc['Engine_no']=re.findall('[a-zA-Z]{1,3}[0-9].*[0-9]{3,6}',i)[0]
            continue
        elif re.search('E NO', i) is not None: 
            eng=re.search("[a-zA-Z]{1,3}[0-9].*[0-9]{3,6}",i)
            if eng is not None:
                eng = i[eng.start():eng.end()]
                dicc['Engine_no']=eng
            continue
                
        ##### Registration Date #######
        # TRY: 1  #
        elif re.search('REG. DT', i) is not None: 
            reg_date=re.search("[0-9]{1,2}[/][0-9]{1,2}[/][0-9]{1,4}",i)
            if reg_date is not None:
                reg_date = i[reg_date.start():reg_date.end()]
                dicc['Register_date']=reg_date
            continue
        
        
        #########  NAME ###########
        elif (re.search('NAME', field)) is not None: 
            field = field[re.search('NAME', field).end():]
            name=re.search("[a-zA-Z].*[a-zA-Z]",field)
            if name is not None:
                name = field[name.start():name.end()]
                dicc['Name']=name
            continue
        # TRY:-2 #
        elif re.search('Name', field) is not None and dicc['Name']=='Not Found' : 
            field = field[re.search('Name', field).end():]
            name=re.search("[a-zA-Z].*[a-zA-Z]",field)
            if name is not None:
                name = field[name.start():name.end()]
                dicc['Name']=name
            continue
    final_data.append(dicc)
    #print(dicc)
ordered_list=["Registration_no","Engine_no","Chasis_no","Register_date","Name"] #list object calls by index but dict object calls items randomly
wb=Workbook("Output.xlsx")
ws=wb.add_worksheet("New Sheet") #or leave it blank, default name is "Sheet 1"
first_row=0
for header in ordered_list:
    col=ordered_list.index(header) # we are keeping order.
    ws.write(first_row,col,header) # we have written first row which is the header of worksheet also.
row=1
for j in final_data: 
    #print(j)
    for _key,_value in j.items():
        col=ordered_list.index(_key)
        ws.write(row,col,_value)
    row+=1 #enter the next row
wb.close()
pd.read_excel("Output.xlsx")