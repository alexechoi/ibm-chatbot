from flask import Flask, request, jsonify
from chatbot import answer_question, knowledge_base
import os
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
    