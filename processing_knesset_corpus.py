import json
import os
import re
from sys import argv
from docx import Document
import matplotlib.pyplot as plt
from collections import Counter
import math

class Protocol:
    def __init__(self,protocol_name, knesset_num, protocol_type, protocol_num=-1, all_speakers=[], all_sentences=[], all_tokens=[]):
        self.protocol_name=protocol_name
        self.knesset_num =knesset_num
        self.protocol_type=protocol_type
        self.protocol_num=protocol_num
        self.all_speakers=all_speakers
        self.all_sentences=all_sentences
        self.all_tokens=all_tokens

    def ToString(self):
        return "protocol name = " + self.protocol_name + " knesset num= " + str(self.knesset_num) + " protocol type= " + self.protocol_type + " protocol num= " +str(self.protocol_num) 

    def Get_protocol_name(self):
        return self.protocol_name
    
    def Get_knesset_num(self):
        return self.knesset_num
    
    def Get_protocol_type(self):
        return self.protocol_type
    
    def Get_protocol_num(self):
        return self.protocol_num

    def Set_protocol_num(self,protocol_num):
        self.protocol_num=protocol_num
    
    def Set_all_speakers(self,all_speakers):
        self.all_speakers=all_speakers

    def Set_all_sentences(self,all_sentences):
        self.all_sentences=all_sentences

    def Set_all_tokens(self,all_tokens):
        self.all_tokens=all_tokens
    
        

class Sentence:
    def __init__(self,content, tokens_list, sentence_type, sentence_length):
        self.content=content
        self.tokens_list=tokens_list
        self.sentence_type=sentence_type
        self.sentence_length=sentence_length


def read_document(file_path):
    doc = Document(file_path)
    doc_text = ""
    doc_by_paragraph = []
    #The whole content of the document
    for para in doc.paragraphs: 
        doc_text += para.text + " "
        doc_by_paragraph.append(para)
    return doc_text, doc_by_paragraph

def export_data_from_name(file_name):
    data = re.split(r"_", file_name)
    knesset_num = int(data[0])
    if data[1]=="ptm":
        protocol_type="plenary"
    elif data[1]=="ptv":
        protocol_type="committee"
    
    return Protocol(file_name, knesset_num, protocol_type)

def export_protocol_num_ptv(doc_text):
    
    num = re.search(r" מס'[ ]+", doc_text)
    if num == None:
        return -1
    num_findall = re.findall(" מס'[ ]+", doc_text)
    num_index = num.start()+len(num_findall[0])
    end_num_index = re.search(r"[ |\,]+", doc_text[num_index:])
    num_string = doc_text[num_index: num_index+end_num_index.start()]
    try:
        number = int(num_string)
        return number
    except ValueError:
        return -1

def word_to_number(num_by_words):
    numbers = {"אחת": 1, "אחד":1,
                "שתיים": 2, "שניים":2,
                "שלוש": 3, "שלושה":3, "שלושת":3,
                "ארבע": 4, "ארבעה":4, "ארבעת":4,
                "חמש": 5, "חמישה":5, "חמשת":5,
                "שש": 6, "שישה":6, "ששת":6,
                "שבע": 7, "שבעה":7, "שבעת":7,
                "שמונה": 8, "שמונת":8, 
                "תשע": 9, "תשעה":9, "תשעת":9,
                "עשר": 10, "עשירית":10, "עשרה":10,
                "עשרים":20,"חמישים":50, "שישים":60, "שמונים":80,
                "מאה":100, "מאתיים":200,
                "אלף":1000, "אלפיים":2000
               }

    return numbers.get(num_by_words, None)

def export_protocol_num_ptm(doc_text):
    
    num = re.search(r"הישיבה[ ]+", doc_text)
    num_findall = re.findall("הישיבה[ ]+", doc_text)
    num_index = num.start()+len(num_findall[0])
    end_num_index = re.search(r"[ ]+", doc_text[num_index:])
    num_string = doc_text[num_index: num_index+end_num_index.start()]
    words_of_num = re.split(r"\-", num_string)
    for i,word in enumerate(words_of_num):
        if word[0]=='ה':
            words_of_num[i]=word[1:]
        if word[0]=='ו':
            words_of_num[i]=word[1:]
    
    real_num=0
    for word in words_of_num:
        if word=='אלפים':
            real_num*=1000
            continue
        if word=='מאות':
            temp = real_num%10
            real_num -=temp
            temp *= 100
            real_num += temp
            continue
        result = word_to_number(word)
        if result!=None: #in the dictionary
            real_num += result
        else:
            split_num = re.sub(r"ים", "", word)
            temp = word_to_number(split_num)
            if temp != None:
                real_num += temp * 10
            else:
                real_num = -1
                break

    return real_num

def speaker (doc_para, protocol_type):
    maybe_speaker =  re.findall(r"^[<א-ת ()\"\'\\\-]+:[>]*", doc_para.text)
    for run in doc_para.runs:
        if protocol_type=="committee":
            if (len(maybe_speaker)>0) and (not(run.bold)):
                return doc_para.text
            else:
                maybe_speaker2 = re.findall(r"^[<>א-ת ()\"\'\\\-]+:[א-ת <>]*",doc_para.text)
                if (len(maybe_speaker2)>0) and (not(run.bold)):
                    return doc_para.text
                else:
                    return None
        else: 
            if (len(maybe_speaker)>0):# and (run.bold) and (run.underline):
                return doc_para.text
            else:
                return None

def clean_speaker(speaker_name):
    
    clean_name= re.sub(r" \([א-ת \"\-]+\)","", speaker_name) #remove party name
    clean_name = re.sub(r"(<<)[א-ת ]+(>>)", "", clean_name)
    clean_name_split = clean_name.split( )
    if len(clean_name_split)>=2:
        clean_name_2_words = clean_name_split[-2] + " " + clean_name_split[-1]
        clean_name_2_words = re.sub(r"[<>]","", clean_name_2_words)
        return clean_name_2_words
    else:
        clean_name = re.sub(r"[<>]","", clean_name)
        return clean_name


def speaker_text(doc_by_paragraph, protocol_type):
    speaker_name = ""
    first_para_speaker = 0
    for k, para in enumerate(doc_by_paragraph): #find the first speaker in the protocol
        if speaker(para, protocol_type)!=None: #the para represent a speaker name
            first_para_speaker = k
            speaker_name = speaker(para, protocol_type)
            break
    
    all_speakers = []
    speaker_data = []
    paragraphs_of_speaker = []

    for j in range(first_para_speaker+1, len(doc_by_paragraph)): #starts from the next paragraph of the first speaker in the protocol
        if speaker_name!="":
            speaker_name = clean_speaker(speaker_name)
            speaker_data.append([speaker_name])
            speaker_name=""

        if speaker(doc_by_paragraph[j], protocol_type)==None:
            paragraphs_of_speaker.append(doc_by_paragraph[j].text)

        if (speaker(doc_by_paragraph[j], protocol_type)!=None):
            speaker_name = speaker(doc_by_paragraph[j], protocol_type)
            
            if len(re.findall(r"קריאה:",speaker_data[0][0]))>0:
                speaker_data = []
                paragraphs_of_speaker = []
            else:
                speaker_data.append(paragraphs_of_speaker)
                all_speakers.append(speaker_data)
                speaker_data = []
                paragraphs_of_speaker = []

    if j == len(doc_by_paragraph)-1: #for the last speaker
        speaker_data.append(paragraphs_of_speaker)
        all_speakers.append(speaker_data)

    return all_speakers

def replace_dots_with_d_in_numbers(match):
    date_parts = match.group(0).split('.')
    return 'd'.join(date_parts)

def sentences_separation(paragraph):

    list_of_sentences=[]

    paragraph = re.sub(r'\b([א-ת]*[0-9]+\.[0-9]+)(?:\.([0-9]+))?\b', replace_dots_with_d_in_numbers, paragraph) #dates and real numbers
    
    # quatation is not a sentence for us. so we save the chars we split by the sentence with symbols that we are sure not going to be in the protocol
    paragraph = re.sub(r'(\")(?P<d1>[א-ת 0-9()\']*)([?])(?P<d2>[א-ת 0-9()\']*)(\")', '\"\g<d1>q\g<d2>\"', paragraph)
    paragraph = re.sub(r'(\")(?P<d1>[א-ת 0-9()\']*)([!])(?P<d2>[א-ת 0-9()\']*)(\")', '\"\g<d1>e\g<d2>\"', paragraph)
    paragraph = re.sub(r'(\")(?P<d1>[א-ת 0-9()\']*)([.])(?P<d2>[א-ת 0-9()\']*)(\")', '\"\g<d1>d\g<d2>\"', paragraph)
    
    sentences = re.split(r'(?<=\.|\?|\!|\n)',paragraph)

    for s in sentences:
        s = re.sub('q', '?', s)
        s = re.sub('e', '!', s)
        s = re.sub('d', '.', s)
        s = re.sub(r'^[ ]+',"",s)
        if clean_sentences(s) != None:
            list_of_sentences.append(s)
    
    return list_of_sentences

def sentences_of_speakers(all_speakers):
    speaker_sentences=[]
    all_sentences=[]

    for speaker_list in all_speakers:

        speaker_sentences.append(speaker_list[0]) #name of speaker
        sentences=[]
        for paragraph in speaker_list[1]:
            sentences.append(sentences_separation(paragraph))
        speaker_sentences.append(sentences)

        all_sentences.append(speaker_sentences)
        speaker_sentences=[]

    return all_sentences

def clean_sentences(sentence_text):

    if len(re.findall(r'[א-ת]+', sentence_text))>0: #a sentence must have at least one letter
        if re.fullmatch(r'[0-9 א-ת()\'\.,?!@#$%^&*\-=+\/\\\"]+', sentence_text) != None: #a sentence can have only those chars
            if re.search(r'[\.?!]$', sentence_text) != None: # a sentence needs to end with . or ! or ?
                if re.search(r'[\.\,\-\!\?]{2,}', sentence_text) == None: # a sentence can't have 2 speacial chras in a row
                    return sentence_text
                else:
                    return None
            else:
                return None
        else:
            return None
    else:
        return None

def replace_commas_with_comma(match):
    return match.group(0).replace(',', 'comma')

def tokens_seperation(clean_sentence):

    list_of_tokens=[]

    clean_sentence = re.sub(r'\b([א-ת]*[0-9]+\.[0-9]+)(?:\.([0-9]+))?\b', replace_dots_with_d_in_numbers, clean_sentence) #dates and real numbers
    clean_sentence = re.sub(r'(?P<d1>[א-ת]+)(\")(?P<d2>[א-ת]+)\b', r'\g<d1>rt\g<d2>', clean_sentence) #short cuts
    clean_sentence = re.sub(r'\b(\d{1,3}(,\d{3})+)\b', replace_commas_with_comma, clean_sentence) #numbers

    tokens = re.split(r'(\.|\?|\!|\,|\ |\"|\)|\(|\-)',clean_sentence)
    for token in tokens:
        token = re.sub('d', '.', token)
        token = re.sub('rt', '"', token)
        token = re.sub('comma', ',', token)

        if (token!=" ") and (token!=""):
            list_of_tokens.append(token)
    
    return list_of_tokens

def tokens_of_speakers(all_sentences):
        
    speaker_tokens=[]
    all_tokens=[]
    
    for speaker_sentences in all_sentences:
        speaker_tokens.append(speaker_sentences[0]) #name of speaker
        tokens=[]
        for par in speaker_sentences[1]:
            for sen in par:
                num_of_tokens = len(tokens_seperation(sen))
                if num_of_tokens >=4:
                    tokens.append(tokens_seperation(sen))       
        speaker_tokens.append(tokens)
        all_tokens.append(speaker_tokens)
        speaker_tokens=[]
    return all_tokens

def to_json(name_protocol, knesset_number, protocol_type, protocol_number, speaker_name, one_sentence, path_to_jsonl_file):

    json_dic = {"name_protocol: ": name_protocol,
                "knesset_number: ": knesset_number,
                "protocol_type: ": protocol_type,
                "protocol_number: ": protocol_number,
                "speaker_name: ": speaker_name,
                }

    full_s = ""
    for t in one_sentence: #t is a token in a one sentence 
        full_s += t + " "
    if "sentence_text: " not in json_dic: 
        json_dic["sentence_text: "] = full_s
    else:
        json_dic["sentence_text: "] = full_s

    with open(path_to_jsonl_file, mode='a', encoding='utf8') as file:
        json.dump(json_dic, file, ensure_ascii=False)
        file.write('\n')

    file.close()

def write_into_jsonl_file(all_tokens, allProtocols_i, jsonl_file_path):

    for token in all_tokens:
        if len(token[1])==0: #the speaker says nothing so we don't need to save his name
            continue
        
        for s in token[1]: #s is a one sentence - saves in a list
            name_protocol = allProtocols_i.Get_protocol_name()
            knesset_number = allProtocols_i.Get_knesset_num()
            protocol_type = allProtocols_i.Get_protocol_type()
            protocol_number = allProtocols_i.Get_protocol_num()
            speaker_name = token[0]
            one_sentence = s
            to_json(name_protocol, knesset_number, protocol_type, protocol_number, speaker_name, one_sentence, jsonl_file_path)


if __name__ == "__main__":
   
    files_path = argv[1]
    jsonl_file_path = argv[2]

    allProtocols = []

    files_names = os.listdir(files_path)
    for i,name in enumerate (files_names):
        path=files_path 
        full_path=os.path.join(path,name)
        doc_text, doc_by_paragraph=read_document(full_path)
        
        allProtocols.append(export_data_from_name(name))
        if allProtocols[i].Get_protocol_type()=="committee":
            num = export_protocol_num_ptv(doc_text)
            allProtocols[i].Set_protocol_num(num)
        elif allProtocols[i].Get_protocol_type()=="plenary":
            num = export_protocol_num_ptm(doc_text)
            allProtocols[i].Set_protocol_num(num)
        
        all_speakers = speaker_text(doc_by_paragraph, allProtocols[i].Get_protocol_type())
        allProtocols[i].Set_all_speakers(all_speakers)
        
        all_sentences = sentences_of_speakers(all_speakers)
        allProtocols[i].Set_all_sentences(all_sentences)

        all_tokens=tokens_of_speakers(all_sentences)
        allProtocols[i].Set_all_tokens(all_tokens)

        write_into_jsonl_file(all_tokens, allProtocols[i], jsonl_file_path)





