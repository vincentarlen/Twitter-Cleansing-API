# Text Preprocessing API
This is a Flask-based API that provides text preprocessing capabilities. The API is designed to be used to clean raw text data such as tweets before being used for analysis or machine learning tasks

## Getting Started
To get started with the Text Preprocessing API, follow these steps:
1. Clone this repository to your local machine
2. Install the required packages by running pip install -r requirements.txt
3. Start the API by running python Cleansing_API.py
4. Navigate to http://localhost:5000/docs to access the Swagger documentation for the API
5. Make sure the file to be cleaned is a csv file and has a column named 'text'

## ENDPOINTS

### POST /text-processing
This endpoint accepts a text string as input and returns a cleaned version of the text.

### POST /text-processing-file
This endpoint accepts a CSV file with a text column, preprocesses the tweets in the file, and stores the cleaned tweets in a SQLite database.
#### RESPONSE
A string indicating that the data has been cleaned and stored in the database.

## Preprocessing Steps
The API performs the following preprocessing steps:
1. Removes unnecessary characters such as URL, RT, USER, and emoji
2. Removes punctuation
3. Fixes spelling using new_kamusalay dictionary

## Depedencies
* Flask
* Pandas
* re
* sqlite3
* flasgger
