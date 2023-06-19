import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from sklearn.feature_extraction.text import CountVectorizer
from fuzzywuzzy import fuzz
from typing import Any, Text, Dict, List
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import torch
import re

# Load summarization pipeline
summarizer = pipeline('summarization', model='t5-small')

# Load sentence-transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def capitalize_response(response):
    return re.sub(r"(?<=\.\s)(\w+)", lambda m: m.group().capitalize(), response.capitalize())

class ActionExplainCourse(Action):
    def name(self) -> Text:
        return "action_explain_course"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course_name = tracker.get_slot("course_name")
        try:
            # Load the data
            xls = pd.ExcelFile('dataset.xlsx')
            df_list = []
            for sheet_name in xls.sheet_names:
                if fuzz.token_set_ratio(course_name.lower(), sheet_name.lower()) > 70:
                    df = xls.parse(sheet_name)
                    df['Course_Name'] = sheet_name
                    df_list.append(df)

            if df_list:
                data = pd.concat(df_list, ignore_index=True)
                
                # Get course info from 'About this course' page
                about_course_info = data[data['Page Title'].str.lower().str.contains('about this course')]

                if not about_course_info.empty:
                    resources = about_course_info.filter(like='Resource').dropna(axis=1)
                    resources_text = [" ".join(row) for row in resources.values]
                    full_response = " ".join(resources_text)
                    sentences = full_response.split('. ')
                    
                    # calculate embeddings for the user's query and all sentences in the resources
                    course_name_embedding = model.encode(course_name, convert_to_tensor=True)
                    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
                    
                    # calculate cosine similarities of sentences in the resources with the user's query
                    cosine_scores = util.pytorch_cos_sim(course_name_embedding, sentence_embeddings)[0]
                    
                    # get top k sentences with the highest cosine similarity
                    k = min(5, len(cosine_scores))
                    top_results = torch.topk(cosine_scores, k=k)
                    response_sentences = [sentences[index] for index in top_results.indices]
                    
                    # join the sentences into a single text and summarize it
                    text_to_summarize = " ".join(response_sentences)
                    summary = summarizer(text_to_summarize, max_length=150, min_length=30, do_sample=False)
                    response = summary[0]['summary_text']
                else:
                    response = f"I'm sorry, I could not find any information on {course_name}."
            else:
                response = f"No matching sheets found for {course_name}."

        except Exception as e:
            response = f"Sorry, I encountered an error: {str(e)}"

        dispatcher.utter_message(capitalize_response(response))
        return []


class ActionInquiryAboutTopic(Action):
    def name(self):
        return "action_inquiry_about_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        topic = tracker.get_slot("topic")
        
        try:
            # Load the data
            xls = pd.ExcelFile('dataset.xlsx')
            df_list = []
            for sheet_name in xls.sheet_names:
                df = xls.parse(sheet_name)
                df['Course_Name'] = sheet_name
                df_list.append(df)

            data = pd.concat(df_list, ignore_index=True)

            vectorizer = CountVectorizer()
            vectorizer.fit([topic])
            topic_keywords = vectorizer.get_feature_names_out()

            # Filter rows where page title contains any of the topic keywords
            topic_info = data[data['Page Title'].apply(lambda x: isinstance(x, str) and any(k in x.lower().split() for k in topic_keywords))]

            if not topic_info.empty:
                resources = topic_info.filter(like='Resource').dropna(axis=1)
                resources_text = [" ".join(row) for row in resources.values]
                full_response = " ".join(resources_text)
                sentences = full_response.split('. ')
                
                # calculate embeddings for the user's query and all sentences in the resources
                topic_embedding = model.encode(topic, convert_to_tensor=True)
                sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
                
                # calculate cosine similarities of sentences in the resources with the user's query
                cosine_scores = util.pytorch_cos_sim(topic_embedding, sentence_embeddings)[0]
                
                # get top k sentences with the highest cosine similarity
                k = min(5, len(cosine_scores))
                top_results = torch.topk(cosine_scores, k=k)
                response_sentences = [sentences[index] for index in top_results.indices]
                
                # join the sentences into a single text and summarize it
                text_to_summarize = " ".join(response_sentences)
                summary = summarizer(text_to_summarize, max_length=150, min_length=30, do_sample=False)
                response = summary[0]['summary_text']
            else:
                response = f"I'm sorry, I could not find any information on {topic}."

        except Exception as e:
            response = f"Sorry, I encountered an error: {str(e)}"

        dispatcher.utter_message(capitalize_response(response))
