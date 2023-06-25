import torch
from torch import nn
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import BertTokenizerFast, AutoModel
import numpy as np
import pandas as pd
import re
import random
from transformers import pipeline
from transformers import RobertaTokenizer, RobertaModel
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import util
from sklearn.preprocessing import LabelEncoder
import json

# Define the BERT_Arch class here
class BERT_Arch(nn.Module):
    def __init__(self, bert):
        super(BERT_Arch, self).__init__()
        self.bert = bert
        self.dropout = nn.Dropout(0.2)
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(768, 512)
        self.fc2 = nn.Linear(512, 256)
        # Assuming num_classes = 5, please change if it's different
        self.fc3 = nn.Linear(256, 9) 
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, sent_id, mask):
        cls_hs = self.bert(sent_id, attention_mask=mask)[0][:, 0]
        x = self.fc1(cls_hs)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc3(x)
        x = self.softmax(x)
        return x

app = Flask(__name__)
CORS(app)

# Load the Roberta tokenizer
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
# Import Roberta pretrained model
bert = RobertaModel.from_pretrained('roberta-base')

# Instantiate your custom model
model = BERT_Arch(bert)

# Load JSON data file
with open("intents.json", "r") as file:
    data = json.load(file)

# Extract intents from the JSON data
intents = [i['tag'] for i in data['intents']]

# Label Encoder
le = LabelEncoder()

# Fit the LabelEncoder with the intents
le.fit(intents)

# Load the trained model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the model state
model_path = "model1.pth"
state_dict = torch.load(model_path, map_location=torch.device('cpu' if not torch.cuda.is_available() else 'cuda'))
model.load_state_dict(state_dict)

model = model.to(device)
model.eval()

# Function to get the intent from a message
def get_intent(message):
    inputs = tokenizer(message, padding=True, truncation=True, return_tensors="pt")
    
    print(type(inputs))
    for k, v in inputs.items():
        print(f"{k}: {type(v)}")
    
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs)
    logits = model(**inputs)
    intent_idx = torch.argmax(logits, dim=1).item()
    return le.inverse_transform([intent_idx])[0]

def get_prediction(text):
    text = re.sub(r'[^a-zA-Z ]+', '', text)
    test_text = [text]

    tokens_test_data = tokenizer(
        test_text,
        padding=True,
        truncation=True,
        return_tensors='pt'
    )
    
    print(type(tokens_test_data))
    for k, v in tokens_test_data.items():
        print(f"{k}: {type(v)}")
    
    input_ids = tokens_test_data['input_ids'].to(device)
    attention_mask = tokens_test_data['attention_mask'].to(device)

    with torch.no_grad():
        logits = model(input_ids, attention_mask)

    preds = torch.argmax(logits, dim=1).detach().cpu().numpy()
    intent = le.inverse_transform(preds)[0]
    print("Intent Identified:", intent)
    return intent

def get_response(message):
    intent = get_prediction(message)

    # Define the course inquiry intents
    course_inquiry_intents = [
        "course_enquiry_ai", 
        "course_enquiry_datascience", 
        "course_enquiry_cyber", 
        "course_enquiry_cloud", 
        "course_enquiry_designthinking"
    ]

    if intent in course_inquiry_intents:
        # Match Intents
        
        if intent == "course_enquiry_ai":
            intent = "Artificial Intelligence"
        if intent == "course_enquiry_datascience":
            intent = "Data Science"
        if intent == "course_enquiry_cyber":
            intent = "Cyber"
        if intent == "course_enquiry_cloud":
            intent = "Cloud"
        if intent == "course_enquiry_designthinking":
            intent = "Enterprise Design Thinking"
        
        action = ActionInquiryAboutTopic()
        result = action.run(intent)
    else:
        # If the intent is not a course enquiry, find a response in data['intents']
        for i in data['intents']:
            if i["tag"] == intent:
                result = random.choice(i["responses"])
                break

    print(f"Response: {result}")
    return "Intent: " + intent + '\n' + "Response: " + result

# Load summarization pipeline
summarizer_pipeline = pipeline('summarization', model='t5-small')

# Load sentence-transformer model
sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

class ActionInquiryAboutTopic:
    def __init__(self):
        pass

    def name(self):
        return "action_inquiry_about_topic"

    def run(self, intent):
        # Define a dictionary mapping each intent to a sheet name
        sheet_name_dict = {
            "Cloud": "1 - Cloud Computing",
            "Artificial Intelligence": "2 - AI Artificial Intelligence",
            "Cyber": "3 - Threat Intelligence Cyber",
            "Data Science": "4 - Data Science",
            "Enterprise Design Thinking": "5 - Enterprise Design Thinking"
        }
        
        topic = intent  # In your context, topic and intent are the same
        sheet_name = sheet_name_dict[topic]
        
        try:
            # Load the data
            xls = pd.ExcelFile('dataset.xlsx')
            df = xls.parse(sheet_name)
            df['Course_Name'] = sheet_name
            
            vectorizer = CountVectorizer()
            vectorizer.fit([topic])
            topic_keywords = vectorizer.get_feature_names_out()

            # Filter rows where page title contains any of the topic keywords
            topic_info = df[df['Page Title'].apply(lambda x: isinstance(x, str) and any(k in x.lower().split() for k in topic_keywords))]

            if not topic_info.empty:
                resources = topic_info.filter(like='Resource').dropna(axis=1)
                resources_text = [" ".join(row) for row in resources.values]
                full_response = " ".join(resources_text)
                sentences = full_response.split('. ')
                
                # calculate embeddings for the user's query and all sentences in the resources
                topic_embedding = sentence_transformer_model.encode(topic, convert_to_tensor=True)
                sentence_embeddings = sentence_transformer_model.encode(sentences, convert_to_tensor=True)
                
                # calculate cosine similarities of sentences in the resources with the user's query
                cosine_scores = util.pytorch_cos_sim(topic_embedding, sentence_embeddings)[0]
                
                # get top k sentences with the highest cosine similarity
                k = min(5, len(cosine_scores))
                top_results = torch.topk(cosine_scores, k=k)
                response_sentences = [sentences[index] for index in top_results.indices]
                
                # join the sentences into a single text and summarize it
                text_to_summarize = " ".join(response_sentences)
                summary = summarizer_pipeline(text_to_summarize, max_length=150, min_length=30, do_sample=False)
                response = summary[0]['summary_text']
            else:
                response = f"I'm sorry, I could not find any information on {topic}."
            
        except Exception as e:
            response = f"Sorry, I encountered an error: {str(e)}"

        return capitalize_response(response)

def capitalize_response(response):
    return response[0].capitalize() + response[1:]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    message = data['message']
    response = get_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)