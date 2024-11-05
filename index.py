from flask import Flask, request

app = Flask(__name__)

def choose_option(n, text):
    text_list = text.split("*")
    response = text_list[-n].strip() if len(text_list) >= n else ""
    return response

# USSD logic for Africa's Talking
@app.route('/', methods=['POST', 'GET'])
def ussd():
    # Get the variables sent via POST from Africa's Talking
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "")

    # Split the text input to manage user input and navigation in the USSD session
    text_list = text.split("*")
    user_response = text_list[-1].strip() if text_list else ""

    # Menu flow based on user response
    if user_response == "":
        # First interaction - display main menu
        response = "CON Takulandirani ku UmunthuAI\n"
        response += "1. Kulembetsa\n"
        response += "2. Akawunti\n"
        response += "0. Kutuluka\n"
    elif user_response == '1' and len(text_list) == 1:
        # User selected "1. Kulembetsa" - register option, prompt for password
        response = "CON Lembani nambala yanu yachinsisi:\n"
        response += "0. Kutuluka\n"
    elif user_response == choose_option(1, text) and len(text_list) == 2:
        # User entered a password, ask to confirm password
        response = "CON Sindikizani nambala yanu yachinsisi:\n"
        response += "0. Kutuluka\n"
    elif user_response == choose_option(1, text) and len(text_list) == 3:
        # Password confirmed, proceed with logged-in actions
        response = "CON Funsani funso lililonse la malamulo:\n"
        response += "0. Kutuluka\n"
    elif user_response == '2':
        # User selected "2. Akawunti" - account management option
        response = "CON Akawunti yanu ikupezeka pano.\n"
        response += "0. Kutuluka\n"
    elif user_response == '0':
        # User selected "0. Kutuluka" - exit
        response = "END Zikomo! Mwatsanzika bwino.\n"
    else:
        # Invalid option or unknown input
        response = "END Mwasankha molakwika. Chonde yesaninso.\n"

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
