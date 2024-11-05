from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv
app = Flask(__name__)
CORS(app)

load_dotenv()
# MongoDB setup
MONGO_URI=os.getenv('MONGO_URI')
MONGODB_URI=client = MongoClient(MONGO_URI)
db = client["ussd_chatbot"]
users_collection = db["users"]

# USSD states
STATE_REGISTER_NAME = "register_name"
STATE_REGISTER_GENDER = "register_gender"
STATE_REGISTER_AGE = "register_age"
STATE_REGISTER_PASSWORD = "register_password"
STATE_REGISTER_CONFIRM_PASSWORD = "register_confirm_password"
STATE_LOGIN = "login"
STATE_CHAT = "chat"

@app.route("/")
def home():
    return "Environment Variables Loaded Successfully!"
@app.route("/", methods=["POST"])
def ussd():
    session_id = request.form.get("sessionId")
    phone_number = request.form.get("phoneNumber")
    text = request.form.get("text").strip()

    # Initialize response with a default message
    response = "END An unexpected error occurred. Please try again."

    # Get user from MongoDB
    user = users_collection.find_one({"phone_number": phone_number})

    # Split the text to navigate through the inputs
    inputs = text.split("*")

    if not user:
        # Registration Flow
        if len(inputs) == 1:
            # Ask for the full name
            response = "CON Welcome to Chatbot! Please enter your full name:"
            users_collection.insert_one({
                "phone_number": phone_number,
                "state": STATE_REGISTER_NAME,
                "temp_data": {}  # Temporary data storage during registration
            })
        else:
            temp_data = user.get("temp_data", {})
            if user["state"] == STATE_REGISTER_NAME:
                # Save full name and ask for gender
                temp_data["full_name"] = inputs[1]
                users_collection.update_one({"phone_number": phone_number}, {
                    "$set": {"state": STATE_REGISTER_GENDER, "temp_data": temp_data}
                })
                response = "CON Select your gender:\n1. Male\n2. Female"
            elif user["state"] == STATE_REGISTER_GENDER:
                # Save gender and ask for age
                temp_data["gender"] = "Male" if inputs[1] == "1" else "Female"
                users_collection.update_one({"phone_number": phone_number}, {
                    "$set": {"state": STATE_REGISTER_AGE, "temp_data": temp_data}
                })
                response = "CON Enter your age:"
            elif user["state"] == STATE_REGISTER_AGE:
                # Save age and ask for password
                temp_data["age"] = inputs[1]
                users_collection.update_one({"phone_number": phone_number}, {
                    "$set": {"state": STATE_REGISTER_PASSWORD, "temp_data": temp_data}
                })
                response = "CON Set your password:"
            elif user["state"] == STATE_REGISTER_PASSWORD:
                # Save password and ask for password confirmation
                temp_data["password"] = inputs[1]
                users_collection.update_one({"phone_number": phone_number}, {
                    "$set": {"state": STATE_REGISTER_CONFIRM_PASSWORD, "temp_data": temp_data}
                })
                response = "CON Confirm your password:"
            elif user["state"] == STATE_REGISTER_CONFIRM_PASSWORD:
                # Confirm password and complete registration
                if inputs[1] == temp_data["password"]:
                    # Save final user details and move to login state
                    users_collection.update_one({"phone_number": phone_number}, {
                        "$set": {
                            "state": STATE_LOGIN,
                            "full_name": temp_data["full_name"],
                            "gender": temp_data["gender"],
                            "age": temp_data["age"],
                            "password": temp_data["password"],
                            "temp_data": {}  # Clear temporary data
                        }
                    })
                    response = "CON Registration complete! Please enter your password to log in:"
                else:
                    response = "CON Passwords did not match. Set your password again:"
                    users_collection.update_one({"phone_number": phone_number}, {
                        "$set": {"state": STATE_REGISTER_PASSWORD, "temp_data": temp_data}
                    })
    else:
        # Login and Chat Flow
        if user["state"] == STATE_LOGIN:
            # Ask for password if not provided yet
            if len(inputs) == 1:
                response = "CON Welcome back! Please enter your password to log in:"
            elif inputs[1] == user["password"]:
                # Password is correct, move to chat state
                users_collection.update_one({"phone_number": phone_number}, {
                    "$set": {"state": STATE_CHAT}
                })
                response = "CON Login successful! Start chatting below. Type 'exit' to log out."
            else:
                response = "CON Incorrect password. Try again:"
        elif user["state"] == STATE_CHAT:
            # Chatting mode - let users chat until they type 'exit'
            if text.lower() == "exit":
                users_collection.update_one({"phone_number": phone_number}, {
                    "$set": {"state": STATE_LOGIN}
                })
                response = "END You have logged out. Thank you for using the chatbot!"
            else:
                response = f"CON You said: {text}. Type 'exit' to end chat."

    return response
if __name__ == "__main__":
    app.run(debug=True)
