import os
import json
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample greetings and goodbyes
greetings = ["Good day", "How are you?", "What's up?", "Hail and Well Met!"]
goodbyes = ["Adieu", "See ya!", "Goodbye", "Have a great day", "Bye!"]

# JSON file to store the dictionary
definitions_file = 'definitions.json'

# Load or initialize the dictionary
if os.path.exists(definitions_file):
    with open(definitions_file, 'r') as file:
        definitions = json.load(file)
else:
    # Initialize with some example data (you can remove or edit this)
    definitions = {
        "Futurism": {
            "definitions": [
                "A movement that emphasizes themes of the future, technology, speed, and change."
            ],
            "synonyms": ["Future Movement"]
        },
        "Shakespeare": {
            "definitions": [
                "An iconic English playwright known for his influential plays and sonnets."
            ],
            "synonyms": ["Bard", "William Shakespeare"]
        }
    }

def find_word(input_word):
    """
    Return the 'official' key if input_word matches the word itself
    or any of its synonyms (case-insensitive).
    """
    for w, data in definitions.items():
        if w.lower() == input_word.lower():
            return w
        # Check synonyms
        if input_word.lower() in [syn.lower() for syn in data.get('synonyms', [])]:
            return w
    return None

def save_definitions():
    """Save the in-memory definitions dictionary to definitions.json."""
    with open(definitions_file, 'w') as f:
        json.dump(definitions, f, indent=4)

@app.route('/')
def index():
    """
    Show a home page with a random greeting.
    Provide links for searching, adding words, etc.
    """
    greeting = random.choice(greetings)
    return render_template('index.html', greeting=greeting)

@app.route('/search', methods=['GET', 'POST'])
def search_word():
    """
    A page where users can search for a word or synonym.
    If found, redirect to show_definitions page for that word.
    Otherwise, show an error message.
    """
    if request.method == 'POST':
        user_input = request.form['search_term'].strip()
        word_found = find_word(user_input)
        if word_found:
            return redirect(url_for('show_definitions', word=word_found))
        else:
            error_msg = f"'{user_input}' is not in the dictionary."
            return render_template('search_word.html', error_msg=error_msg)
    return render_template('search_word.html')

@app.route('/definitions/<word>')
def show_definitions(word):
    """
    Displays the definitions and synonyms of a given word.
    """
    data = definitions.get(word)
    if not data:
        return f"'{word}' not found in the dictionary.", 404
    return render_template('show_definitions.html', word=word, data=data)

@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    """
    Form to add a brand-new word to the dictionary with an initial definition.
    """
    if request.method == 'POST':
        new_word = request.form['new_word'].strip().title()
        new_def = request.form['new_definition'].strip()

        if new_word in definitions:
            msg = f"'{new_word}' already exists in the dictionary."
        else:
            definitions[new_word] = {
                "definitions": [new_def],
                "synonyms": []
            }
            save_definitions()
            msg = f"Word '{new_word}' added successfully."
        return render_template('success.html', message=msg)
    return render_template('add_word.html')

@app.route('/add_definition', methods=['GET', 'POST'])
def add_definition():
    """
    Form to add a new definition to an existing word.
    """
    if request.method == 'POST':
        existing_word = request.form['existing_word'].strip()
        new_def = request.form['new_definition'].strip()
        found_key = find_word(existing_word)

        if found_key:
            definitions[found_key]['definitions'].append(new_def)
            save_definitions()
            msg = f"New definition added for '{found_key}'."
        else:
            msg = f"'{existing_word}' is not in the dictionary."
        return render_template('success.html', message=msg)
    return render_template('add_definition.html')

@app.route('/add_synonyms', methods=['GET', 'POST'])
def add_synonyms():
    """
    Form to add synonyms to an existing word.
    """
    if request.method == 'POST':
        existing_word = request.form['existing_word'].strip()
        synonyms_str = request.form['new_synonyms'].strip()
        found_key = find_word(existing_word)

        if found_key:
            # Parse comma-separated synonyms
            synonyms_list = [s.strip().title() for s in synonyms_str.split(',') if s.strip()]
            definitions[found_key]['synonyms'].extend(synonyms_list)
            # Remove duplicates
            definitions[found_key]['synonyms'] = list(set(definitions[found_key]['synonyms']))
            save_definitions()
            msg = f"Synonyms added for '{found_key}'."
        else:
            msg = f"'{existing_word}' is not in the dictionary."
        return render_template('success.html', message=msg)
    return render_template('add_synonyms.html')

@app.route('/search_all', methods=['GET', 'POST'])
def search_all():
    """
    A broader search: finds all words that contain the search term
    in their name or synonyms.
    """
    if request.method == 'POST':
        term = request.form['search_term'].strip().lower()
        results = []
        for w, data in definitions.items():
            if term in w.lower():
                results.append(w)
            else:
                # Check synonyms
                if any(term in syn.lower() for syn in data.get('synonyms', [])):
                    results.append(w)
        return render_template('search_all_results.html', results=results, search_term=term)
    return render_template('search_all.html')

@app.route('/goodbye')
def goodbye():
    """Optional route to just say a random goodbye."""
    return random.choice(goodbyes)

if __name__ == '__main__':
    app.run(debug=True)
