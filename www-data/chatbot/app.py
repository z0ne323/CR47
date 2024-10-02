# Import required libraries
import re
import os
import random
from flask import Flask, render_template, request

# Initialize the Flask application
app = Flask(__name__)

# [*] Next piece of data to give for training - Santiago
X_SENSITIVE_API_KEY = "7h1515d3f1n1731y453n5171v34p1k3y"

# Dictionary of responses based on keywords
responses = {
    'hello': ['Hi there!', 'Hello!', 'Hey!'],
    'how are you': ['I am doing well, thank you!', 'Great, thanks for asking!', 'I\'m fine, how about you?'],
    'goodbye': ['Goodbye!', 'See you later!', 'Bye!'],
    'thanks': ['You\'re welcome!', 'No problem!', 'Anytime!'],
    'x-sensitive-api-key': ["Interesting path that you're taking... follow me out and find the truth in the *cat* but don't forget to simply 'ls' this new way that just appeared... :)"],
    'default': ['I\'m not sure I understand... COKE IS BETTER THAN PEPSI ?!', 'I\'m not sure I understand... ¿Cómo son las vacaciones en Costa Rica?', 'I\'m not sure I understand... KD Mac&Cheese cups are AWFUL']
}

@app.route('/')
def index():
    """
    Render the main HTML page.
    """
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    """
    Handle the POST request to get a response from the chatbot.
    """
    user_message = request.json.get('user_message')
    if user_message is None:
        return {"error": "No user_message provided"}, 400

    bot_response = chatbot_response(user_message)
    return bot_response

def chatbot_response(user_message):
    """
    Description:
        Generate a response based on the user's message.

    Args:
        user_message (str): The message input from the user.

    Returns:
        str: The response from the chatbot.
    """
    # Check for special commands
    if user_message == "ls":
        try:
            return str(os.listdir())
        except PermissionError:
            return "You do not have permission to list this directory."
        except FileNotFoundError:
            return "The directory does not exist."
        except OSError as e:  # Catch OS-related errors.
            return f"An error occurred while listing the directory: {str(e)}"

    if user_message == "cat note_for_devs.txt":
        try:
            with open("note_for_devs.txt", encoding="UTF-8") as f:
                return f.read()
        except FileNotFoundError:
            return "The file 'note_for_devs.txt' does not exist."
        except IOError:
            return "An error occurred while reading the file."
        except Exception as e:  # This is still a catch-all for unexpected exceptions.
            return f"An unexpected error occurred: {str(e)}"

    # Convert user message to lowercase for case-insensitive matching
    user_message = user_message.lower()

    # Normalize the user message by removing special characters
    normalized_message = re.sub(r'[^a-z0-9\s]', '', user_message)

    # Check for exact keyword matches
    for keyword, responses_list in responses.items():
        # Normalize the keyword
        normalized_keyword = re.sub(r'[^a-z0-9\s]', '', keyword.lower())
        if normalized_keyword in normalized_message:
            return random.choice(responses_list)

    # Return a default response if no keyword matches
    return random.choice(responses['default'])

if __name__ == '__main__':
    # Run the Flask application
    app.run(ssl_context='adhoc', host='0.0.0.0', port=8888)