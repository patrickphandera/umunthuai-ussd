from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/ussd', methods=['POST'])
def ussd():
    # Retrieve the POST data sent by the USSD gateway
    session_id = request.form.get('sessionId', '')
    service_code = request.form.get('serviceCode', '')
    phone_number = request.form.get('phoneNumber', '')
    text = request.form.get('text', '')

    # Parse user input
    if text == '':
        response = "CON Welcome to the USSD app\n"
        response += "1. Check Balance\n"
        response += "2. Transfer Money\n"
    elif text == '1':
        response = "END Your balance is K1000"
    elif text == '2':
        response = "CON Enter recipient phone number:"
    elif text.startswith('2*'):
        parts = text.split('*')
        if len(parts) == 2:
            response = "CON Enter amount to transfer:"
        elif len(parts) == 3:
            response = f"END You have transferred K{parts[2]} to {parts[1]}"
        else:
            response = "END Invalid input. Try again."
    else:
        response = "END Invalid option. Try again."

    return make_response(response, 200)

if __name__ == '__main__':
    app.run(debug=True)
