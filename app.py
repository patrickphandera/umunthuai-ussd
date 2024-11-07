from flask import Flask, request
import random

app = Flask(__name__)

# Mock data for simulation
mock_users = {}  # Stores user data as {"phone_number": {"password": "password"}}
mock_games = [
    {"id": 1, "league": "Simama", "teams": "Mightty wonderers vs Blue Eagles", "price": 50},
    {"id": 2, "league": "Tnm League", "teams": "Nyasa big bullets vs Mighty wonders", "price": 70},
    {"id": 3, "league": "Tnm League", "teams": "Nyasa big bullets vs Silver strikers", "price": 60},
]

@app.route('/', methods=['POST', 'GET'])
def ussd():
    # Get the parameters from Africa's Talking, defaulting `text` to an empty string if not provided
    session_id = request.form.get("sessionId", "")
    service_code = request.form.get("serviceCode", "")
    phone_number = request.form.get("phoneNumber", "")
    text = request.form.get("text", "")

    # Split the user input based on '*'
    text_array = text.split('*')
    session_level = len(text_array)

    response = ""

    # Step 1: Register or login
    if session_level == 1:
        if phone_number in mock_users:
            response = "CON Enter your password to login:"
        else:
            response = "CON Welcome! Enter a password to register:"

    # Step 2: Handle Registration/Login
    elif session_level == 2:
        password = text_array[1] if len(text_array) > 1 else ""

        if phone_number not in mock_users:
            # Register the user
            mock_users[phone_number] = {"password": password}
            response = "CON Registration successful! Please re-enter your password to confirm login:"
        else:
            # Login validation
            if mock_users[phone_number]["password"] == password:
                response = "CON Login successful! Select a game:\n"
                for idx, game in enumerate(mock_games, 1):
                    response += f"{idx}. {game['league']} - {game['teams']} @ {game['price']} MWK\n"
            else:
                response = "END Incorrect password. Please try again."

    # Step 3: Game Selection
    elif session_level == 3:
        try:
            game_index = int(text_array[2]) - 1
            if 0 <= game_index < len(mock_games):
                selected_game = mock_games[game_index]
                response = f"CON You selected: {selected_game['league']} - {selected_game['teams']}\n"
                response += f"Ticket Price: {selected_game['price']} MWK\n"
                response += "1. Confirm Booking\n2. Cancel"
            else:
                response = "END Invalid selection. Please try again."
        except (IndexError, ValueError):
            response = "END Invalid input. Please try again."

    # Step 4: Confirm or Cancel Booking
    elif session_level == 4:
        if text_array[3] == "1":
            ticket_code = generate_ticket_code()
            response = f"END Booking confirmed! Your ticket code: {ticket_code}"
        else:
            response = "END Booking cancelled."

    else:
        response = "END Invalid input. Please try again."

    # Return the response
    return response, 200

# Function to generate a unique ticket code
def generate_ticket_code():
    return f'TK{random.randint(100000, 999999)}'

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
