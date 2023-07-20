import pandas as pd
import openai
import language_tool_python
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from collections import Counter

# NLTK Data download
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

openai.api_key = ''

# Load spreadsheet
xls = pd.ExcelFile('DATASET')

# Load a sheet into our dataframe
df_list = []
for sheet_name in xls.sheet_names[1:]:
    df = xls.parse(sheet_name)
    df['Course_Name'] = sheet_name  # adding a column with the (name of the excel sheet)
    df_list.append(df)

# Concatenate all data into one dataframe
data = pd.concat(df_list, ignore_index=True)

knowledge_base = {}

for index, row in data.iterrows():
    # Get only those cells which are not nan for all resource columns
    resources = [row['Resource '+str(i)] for i in range(1, 33) if pd.notna(row['Resource '+str(i)])]
    knowledge_base[row['Page Title']] = resources

# Initialize the LanguageTool object for English grammar checks
tool = language_tool_python.LanguageTool('en-US')

# Initialize stop words
stop_words = set(stopwords.words('english'))

def get_most_common_nouns(kb, num):
    counter = Counter()
    for key in kb.keys():
        words = word_tokenize(key)
        words = [word for word in words if word.isalpha()]
        words = [word for word, pos in pos_tag(words) if pos.startswith('NN')]
        words = [word for word in words if word not in stop_words]
        counter.update(words)
    return [item[0] for item in counter.most_common(num)]

common_nouns = get_most_common_nouns(knowledge_base, 50)
manual_keywords = [
    
]


def is_question_relevant(question, kb, common_nouns, manual_keywords):
    # Make the question lowercase for comparison
    question = question.lower()
    question_words = set(word_tokenize(question))

    # Check if any of the keys in the knowledge base are in the question
    for key in kb.keys():
        if key.lower() in question:
            return True

    # Check if any of the common nouns are in the question
    for noun in common_nouns:
        if noun in question_words:
            return True

    # Check if any of the manual keywords are in the question
    for keyword in manual_keywords:
        if keyword in question_words:
            return True

    return True

def correct_grammar(text):
    # Correct all grammar mistakes
    corrected_text = tool.correct(text)
    return corrected_text

def get_relevant_information(question, kb):
    relevant_info = []
    for key in kb:
        if key in question:
            relevant_info.append(' '.join([str(i) for i in kb[key] if i]))
    relevant_info = relevant_info[:5]  # Get the top 5 relevant pieces of information
    return relevant_info

def get_answer_from_gpt4(question, relevant_info):
    prompt = "Answer the following question as if you were a chatbot for IBM: {}. Use the following pieces of information primarily to help you: {}. Do NOT include any information which is not directly relevant to the question and ensure your answer makes grammatical sense. If there question is a greeting or irrelevant to IBM, ONLY respond with \"Hi, I am an IBM Chatbot\"".format(question, ', '.join(relevant_info))
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=prompt,
      max_tokens=150
    )
    answer = response.choices[0].text.strip()
    if answer.startswith('?'): 
        answer = answer[1:].lstrip()
    return answer

def answer_question(question, kb):
    # Check if the question is relevant
    if not is_question_relevant(question, kb, common_nouns, manual_keywords):
        return "I'm sorry, I can only provide information on specific topics."

    # If the question is relevant, try to get an answer from the knowledge base
    answer = get_relevant_information(question, kb)

    if answer:  # if there's an answer in the kb, use it
        # Correct the grammar in the answer
        answer = correct_grammar(' '.join(answer))
    else:  # if there's no answer in the kb, use GPT-4
        answer = get_answer_from_gpt4(question, answer)

    return answer
