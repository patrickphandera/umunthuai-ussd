from flask import Flask, request, jsonify, make_response
import openai
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app and configurations
app = Flask(__name__)
CORS(app)

# Set up OpenAI API key and model
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL")

# System context for OpenAI model
system_context = 'you are a helpful assistant that answers question from user from chichewa constitution of malawi in the form Chapter:<constitution_chapter>,Section:<costitution_section>, <answer_from_chichewa_constititution>'

# Helper function to call OpenAI API with query
def query_model(query):
    try:
        response = openai.chat.completions.create(
        model=MODEL,
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": query },
                ],
            temperature=0,
            )
        generated_text = response.choices[0].message.content
        return generated_text
    except Exception as e:
        return f"Error during API call: {str(e)}"

# USSD endpoint to handle chat without database
@app.route('/', methods=['POST'])
def ussd_chat():
    # Retrieve user input from USSD request
    session_id = request.form.get('sessionId', '')
    phone_number = request.form.get('phoneNumber', '')
    text = request.form.get('text', '')

    # Start the conversation
    if text == "":
        response = "CON Welcome to the USSD Chatbot!\n"
        response += "Type your question to begin."
    else:
        # Forward user input to OpenAI API for a response
        chat_response = query_model(text)

        if "Error" in chat_response:
            response = f"END Sorry, there was an error: {chat_response}"
        else:
            response = f"CON {chat_response}\n\n"
            response += "Reply with another question or type '0' to end."

    # End session if user enters '0'
    if text == "0":
        response = "END Thank you for using the chatbot. Goodbye!"

    # Return USSD response
    return make_response(response, 200, {"Content-Type": "text/plain"})

