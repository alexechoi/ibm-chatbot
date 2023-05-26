import pandas as pd
import openai

openai.api_key = '***REMOVED***'

# Load spreadsheet
xls = pd.ExcelFile('https://cloud-object-storage-cos-static-web-hosting-lcr.s3.eu-de.cloud-object-storage.appdomain.cloud/dataset.xlsx')

# Load a sheet into a DataFrame by iterating over all sheets starting from the second one (index 1)
df_list = []
for sheet_name in xls.sheet_names[1:]:  # skipping the first sheet (index 0) as it's a metadata sheet
    df = xls.parse(sheet_name)
    df['Course_Name'] = sheet_name  # adding a column with the course name
    df_list.append(df)

# Concatenate all data into one DataFrame
data = pd.concat(df_list, ignore_index=True)
data.head()

knowledge_base = {}

for index, row in data.iterrows():
    # Get only those cells which are not nan for all resource columns
    resources = [row['Resource '+str(i)] for i in range(1, 33) if pd.notna(row['Resource '+str(i)])]
    knowledge_base[row['Page Title']] = resources

def get_answer_from_kb(question, kb):
    for key in kb:
        if key in question:
            return ' '.join([str(i) for i in kb[key] if i])  # concatenate all resources related to the key
    return None

def get_answer_from_gpt4(question):
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=question,
      max_tokens=150
    )
    return response.choices[0].text.strip()

def answer_question(question, kb):
    answer = get_answer_from_kb(question, kb)
    if answer is None:  # if there's no answer in the kb, use GPT-4
        answer = get_answer_from_gpt4(question)
    return answer