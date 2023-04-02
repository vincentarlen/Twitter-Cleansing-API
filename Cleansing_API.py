import re
import pandas as pd
import os
import sqlite3
from flask import Flask, jsonify,request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__)

#create folder if not exist 
if not os.path.exists("hasil"):
    os.makedirs("hasil")

kamus = pd.read_csv('new_kamusalay.csv', names=['old','new'], encoding='ISO-8859-1')
kamus_dict = dict(zip(kamus['old'], kamus['new']))

def fix_word(text):
    return ' '.join([kamus_dict[word] if word in kamus_dict else word for word in text.split(' ')])

def remove_unnecessaryChar(text):
    text = re.sub(r'&amp;|amp;|&', 'dan', text) # replace ampersand with dan 
    text = re.sub(r'\\n+', ' ', text) # remove newline
    text = re.sub('&lt;/?[a-z]+&gt;', ' ', text) #remove special character ex:<,>
    text = re.sub(r'#+','#', text) # fix double hashtag | can remove this line to remove # 
    text = re.sub(r'http\S+',' ',text) # remove link 
    text = re.sub(r'(USER+\s?|RT+\s?|URL+\s?)', ' ', text) # remove USER,RT,URL
    text = re.sub(r'x[a-zA-Z0-9]+', ' ', text) # remove emoticon 
    return text

def remove_punctuation(text):
    text = re.sub(r'\?', ' ', text) # remove ? 
    # remove all punctuation except # and % | remove # from the pattern if want to remove # from data
    text = re.sub(r'[^a-zA-Z0-9#%]+', ' ', text) 
    # fix multiple whitespace and replace it with one whitespace, change to lowercase,remove number at first word, remove whitespace in front and back  
    text = re.sub(r' +', ' ', text.lower().lstrip("0123456789").strip()) 
    return text

def preprocessing(text):
    text = remove_unnecessaryChar(text)
    text = remove_punctuation(text)
    text = fix_word(text)
    return text

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host) 
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template,config=swagger_config)

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

        text = request.form.get('text')
        clean_text = preprocessing(text)
        json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': clean_text,
        }
        response_data = jsonify(json_response)
        return response_data

@swag_from("docs/text_processing_file.yml", methods=['POST'])
@app.route('/text-processing-file', methods=['POST'])
def text_processing_file():

    file = request.files['file']
    df = pd.read_csv(file, encoding='ISO-8859-1')
    #remove special character like á \a' ć \c' é \e' í \i' ń \n' ó \o' ś \s' ú \u' ý \y' ź \z' Á \A' 
    df["text"] = df["text"].str.encode('ascii', 'ignore').str.decode('ascii')
    df.drop_duplicates() #remove duplicate data 

    kamus = pd.read_csv('new_kamusalay.csv', names=['old','new'], encoding='ISO-8859-1')
    kamus_dict = dict(zip(kamus['old'], kamus['new']))

    df["hasil"] = df["text"].apply(preprocessing)
    df.replace('', pd.NA, inplace=True) # make empty data as NA 
    df.dropna(inplace=True) # drop every NA data
    df.reset_index(drop=True, inplace=True)
    final = pd.DataFrame({'Tweet':df["hasil"]})
    final.to_csv('hasil/result.csv')
    
    # connect to SQLite database
    conn = sqlite3.connect('hasil/result.db')
    cur = conn.cursor()

    # create table if not exists
    cur.execute('''CREATE TABLE IF NOT EXISTS cleaned_data (tweet VARCHAR)''')

    # insert preprocessed tweets into table
    for tweet in final['Tweet']:
        cur.execute('''INSERT INTO cleaned_data (tweet) VALUES (?)''', (tweet,))

    conn.commit()
    cur.close()

    return 'data sudah bersih dan tersimpan dalam database'

if __name__ == '__main__':
    app.run()
