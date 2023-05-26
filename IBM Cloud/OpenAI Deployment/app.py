from flask import Flask, request, jsonify
from chatbot import answer_question, knowledge_base  # assuming your chatbot functions are in chatbot.py

app = Flask(__name__)

@app.route('/ask', methods=['GET'])
def get_answer():
    question = request.args.get('question', '')  # Get question from URL parameters
    if question:
        answer = answer_question(question, knowledge_base)
        return jsonify({'answer': answer})
    else:
        return jsonify({'error': 'No question provided'}), 400

if __name__ == '__main__':
    # Run the application, making it publicly available on port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)
