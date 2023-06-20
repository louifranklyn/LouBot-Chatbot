# LouBot-Chatbot
Prerequisites:

Python 3.x: Install Python 3.x on your system.
Django: Install Django using pip: pip install django
AIML: Install AIML using pip: pip install python-aiml
NLTK: Install NLTK using pip: pip install nltk
Neo4j: Install Neo4j on your system and set up a Neo4j database. Update the connection parameters (URI, user, password) in the code to match your Neo4j database configuration.
Spacy: Install Spacy using pip: pip install spacy. Download the English language model: python -m spacy download en_core_web_sm
BeautifulSoup: Install BeautifulSoup using pip: pip install beautifulsoup4
Py2neo: Install Py2neo using pip: pip install py2neo

Installation:

Clone the repository or download the source code.
Open a terminal or command prompt and navigate to the project's root directory.
Create a virtual environment (optional but recommended):
Run python3 -m venv venv to create a new virtual environment.
Activate the virtual environment:
On macOS and Linux: source venv/bin/activate
On Windows: venv\Scripts\activate
Install the required dependencies:
Run pip install -r requirements.txt to install all the necessary packages.
Configure the Neo4j database connection:
Open the Django project settings file (chatbot/settings.py).
Update the NEO4J_DATABASES section with your Neo4j database configuration details (URI, user, password).

Apply database migrations:

Run python manage.py migrate to apply the initial database migrations.
Start the Django development server:
Run python manage.py runserver to start the server.
Access the chatbot application:
Open a web browser and visit http://localhost:8000 to access the chatbot interface.
Usage
Open the chatbot interface in a web browser.
Enter your message in the input field and press Enter to send it to the chatbot.
The chatbot will process your input and generate a response.
Continue the conversation by providing more inputs.
To exit the chatbot, close the browser or navigate away from the chatbot interface.

Customization:

You can customize the chatbot's responses and behavior by modifying the AIML files located in the aiml directory. These files define the chatbot's knowledge base and response patterns. Refer to the AIML documentation for more information on creating and modifying AIML files.
