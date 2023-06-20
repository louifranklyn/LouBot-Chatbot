import os, requests, re
import aiml
from glob import glob
import time
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import socket
import string
import aiml
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser
import datetime
import nltk
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.corpus import wordnet
from bs4 import BeautifulSoup
from py2neo import Graph
from neo4j import GraphDatabase
from py2neo import Node, Graph, Relationship
import pytholog as pl


# Set up the connection parameters
uri = "bolt://localhost:7687"
user = "neo4j"
password = "qwerty123"

# Establish a connection to Neo4j
driver = GraphDatabase.driver(uri, auth=(user, password))

# Make your Bot learn aiml files
mybot = aiml.Kernel()
for files in glob('./aimlfiles/*.aiml'):
    mybot.learn(files)

def home(request):
    return render(request, 'home.html')


kb = pl.KnowledgeBase("KB")

knowledge = ['male(ali)',
             'male(ahmed)',
             'female(ayesha)',
             'parent(ali, ahmed)',
             'parent(ahmed, ayesha)',
             'father(X, Y):-male(X), parent(X, Y)']

with open(r'pytholog_kb.pl', 'w') as file:
    for item in knowledge:
        file.write(item + '\n')


def search_person(name):
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User) WHERE u.full_name = $name RETURN COUNT(u) AS count",
            name=name
        )
        count = result.single()["count"]
        return count > 0
    
def search_person_username(username, password):
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User) WHERE u.username = $username AND u.password = $password RETURN COUNT(u) AS count",
            username=username,
            password=password
        )
        count = result.single()["count"]
        return count > 0


def search_person_password(password):
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User) WHERE u.password = $password RETURN COUNT(u) AS count",
            password=password
        )
        count = result.single()["count"]
        return count > 0
    

def search_person_name(username):
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User) WHERE u.username = $username RETURN u.full_name AS full_name",
            username=username
        )
        record = result.single()
        if record is not None:
            full_name = record["full_name"]
            return full_name
        else:
            return False


# Define the function to create a relationship between two persons
def create_relationship(person1, person2, relationship):
        with driver.session() as session:
            session.run(
                "MATCH (p1:User), (p2:User) "
                "WHERE p1.full_name = $person1 AND p2.full_name = $person2 "
                "CREATE (p1)-[r:" + str(relationship) + "]->(p2)",
                person1=person1,
                person2=person2,
                relationship=relationship
            )
            
            
def create_social_network_relationship(person1, person2, relationship, ip_address):
        with driver.session() as session:
            session.run(
                "MATCH (p1:User), (p2:User) "
                "WHERE p1.full_name = $person1 AND p2.full_name = $person2 AND p2.password = $ip_address "
                "CREATE (p1)-[r:" + str(relationship) + "]->(p2)",
                person1=person1,
                person2=person2,
                relationship=relationship,
                ip_address = ip_address
            )


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        valid_username = search_person_username(username, password)
        #valid_password = search_person_password(password)
        if valid_username:
            full_name = search_person_name(username)
            global get_current_user_name #to retrieve the name of logged in person anywhere in program
            variable_name = 'name'
            value = str(full_name)
            get_current_user_name = value
            test_response = mybot.respond(f'My name is {value}', "Louis")
            print(f'My name is {value}')
            print('The test response from AIML file afte sending anonymous message:', test_response)
            mybot.saveBrain("bot_brain.brn")
            return redirect('chatbox')
        else:
            error_message = 'Invalid username or password'
            return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'login.html',{'form':form})

def create_user_credentials(full_name, username, email, password):
    with driver.session() as session:
        # Create the user node and set attributes
        session.run(
            "CREATE (u:User {full_name: $full_name, username: $username, email: $email, password: $password})",
            full_name=full_name,
            username=username,
            email=email,
            password=password
        )
        

def create_ip_address_node(full_name, ip_address):
    with driver.session() as session:
        # Create the user node and set attributes
        session.run(
            "CREATE (u:User {full_name: $full_name, ip_address: $ip_address})",
            full_name=full_name,
            ip_address=ip_address
        )
        

def signup(request):
    if request.method == 'POST':
        fullname = request.POST['fullname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        
        
        _fullname = fullname
        _username = username
        _email = email
        _password = password
        create_user_credentials(_fullname, _username, _email, _password)
        ip_address = getIP()
        create_user_credentials('IP Address', 'NULL', 'NULL', ip_address)
        create_social_network_relationship(_fullname, 'IP Address', 'has_IP_Address', ip_address)
        
        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
        
        
        return redirect('login')
    return render(request, 'signup.html')

def contact(request):
    return render(request, 'contact.html')


def chatbox(request):
    return render(request, 'chatbox.html')


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
    
    
def getDate():
    current_date = datetime.date.today()
    day = current_date.day
    month = current_date.strftime("%B")
    year = current_date.year
    
    bot_response = "Today's date is: ", day,' of ', month,', ', year
    return bot_response

def get_word_definition(word):
    synsets = wordnet.synsets(word)
    if synsets:
        definition = synsets[0].definition()
        return definition
    else:
        return "sorry"

def process_input(input_text):
    tokens = word_tokenize(input_text.lower())
    filtered_tokens = [token for token in tokens if token.isalnum() and token not in stopwords.words('english')]

    word_frequency = nltk.FreqDist(filtered_tokens)

    exclude_words = ['meant', 'meaning', 'definition', 'mean', 'define', 'procedure', 'what is a', 'what is an', 'tell', 'about', 'yourself', 'me']
    filtered_frequency = [(word, freq) for word, freq in word_frequency.items() if word not in exclude_words]

    if len(filtered_frequency) > 0:
        word_to_define = max(filtered_frequency, key=lambda item: item[1])[0]
    else:
        return "sorry"

    definition = get_word_definition(word_to_define)
    response = f"The definition of '{word_to_define}' is: {definition}"
    if definition == 'sorry':
        return 'sorry'
    return response

target_words = ['meant', 'meaning', 'definition', 'mean', 'explain', 'explaination', 'tell me', 'define', 'procedure', 'what is a', 'what is an']


def extract_person_names(message):
    names = []
    tokens = word_tokenize(message)
    tagged_tokens = pos_tag(tokens)
    chunked_tokens = ne_chunk(tagged_tokens)

    for chunk in chunked_tokens:
        if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
            names.append(' '.join(c[0] for c in chunk))

    if len(names) > 1:
        return list(names)
    elif len(names) == 1:
        return '1'
    else:
        return False


def create_tags(sentence):
    tokens = word_tokenize(sentence)
    poss_tagged_list = pos_tag(tokens)

    print(sentence)
    print(tokens)
    print(poss_tagged_list)
    return poss_tagged_list


def Semantics(sentence):
    nodes = []
    relation = []
    tags_list = create_tags(sentence)
    for tag in tags_list:

        if tag[1] == "NNP" or tag[1] == "NNS" or tag[1] == "PRP" or tag[1] == "JJ" or tag[1] == "NN":
            nodes.append(tag[0])

        elif tag[1] == "VBZ" or tag[1] == "VBP" or tag[1] == "JJR" or tag[1] == "VBN" or tag[1] == "VB" or tag[
            1] == "VBP" or tag[1] == "NN" or tag[1] == "IN":
            relation.append(tag[0])
        
        # Start a session
    with driver.session() as session:
        
        # Merge the first node
        result1 = session.run("MERGE (n:User{name: $node1}) RETURN n", node1=nodes[0])

        # Merge the second node
        result2 = session.run("MERGE (m:User{name: $node2}) RETURN m", node2=nodes[1])

        # Match and merge the relationship between the nodes
        #relation_type = relation.replace("'", "\\'")  # Escape single quotes in the relation type
        joined_string = str('_'.join(relation))
        print(f'relationship is: {joined_string} and relation is: {relation}')
        query = """
            MATCH (n:User{name: $node1}), (m:User{name: $node2})
            MERGE (n)-[r:%s]->(m)
            RETURN n, m
        """ % (joined_string)
        result3 = session.run(query, node1=nodes[0], node2=nodes[1])
        # Process the results if needed
        for record in result1:
            print(record)
        for record in result2:
            print(record)
        for record in result3:
            print(record)
            

def Semantics_for_Logged_In_Person(sentence):
    nodes = []
    relation = []
    tags_list = create_tags(sentence)
    for tag in tags_list:

        if tag[1] == "NNP" or tag[1] == "NNS" or tag[1] == "PRP" or tag[1] == "JJ" or tag[1] == "NN":
            nodes.append(tag[0])

        elif tag[1] == "VBZ" or tag[1] == "VBP" or tag[1] == "JJR" or tag[1] == "VBN" or tag[1] == "VB" or tag[
            1] == "VBP" or tag[1] == "NN" or tag[1] == "IN":
            relation.append(tag[0])
        
        # Start a session
    with driver.session() as session:

        # Merge the second node
        result2 = session.run("MERGE (m:Person{name: $node2}) RETURN m", node2=nodes[1])

        # Match and merge the relationship between the nodes
        #relation_type = relation.replace("'", "\\'")  # Escape single quotes in the relation type
        joined_string = str('_'.join(relation))
        print(f'relationship is: {joined_string} and relation is: {relation}')
        query = """
            MATCH (n:User{full_name: $node1}), (m:Person{name: $node2})
            MERGE (n)-[r:%s]->(m)
            RETURN n, m
        """ % (joined_string)
        result3 = session.run(query, node1=get_current_user_name, node2=nodes[1])
        # Process the results if needed
        for record in result2:
            print(record)
        #for record in result3:
         #   print(record)


def get_definition(word):
    synsets = wordnet.synsets(word)
    if synsets:
        definition = synsets[0].definition()
        return definition
    else:
        return None


def linkingPyToAiml(uer_message):
    response = mybot.respond(uer_message)
    word = mybot.getPredicate("searchword")
    definition = None
    if word:
            definition = get_definition(word)
            mybot.setPredicate("definition", definition)
            response = mybot.respond(uer_message)
            if response:
                return HttpResponse(response, content_type='text/plain')
            else:
                response = "Sorry, I couldn't find a definition for that word."
                return HttpResponse(response, content_type='text/plain')
    else:
        resposne = 'My getPredicate function is not getting a value from AIML'
        return HttpResponse(response, content_type='text/plain')
    

def get_from_wikipedia(query, num_sentences=3):
    url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    try:
        # Send a GET request to the Wikipedia page
        response = requests.get(url)
        response.raise_for_status()
        # Parse the HTML response
        soup = BeautifulSoup(response.text, "html.parser")
        # Find the main content element
        content_div = soup.find(id="mw-content-text")
        if content_div:
            # Find the paragraphs within the content element
            paragraphs = content_div.find_all("p")
            if paragraphs:
                # Extract the text from the paragraphs
                text = " ".join([paragraph.get_text() for paragraph in paragraphs])
                # Remove citations and references
                text = re.sub(r"\[\d+\]", "", text)
                # Extract the desired number of sentences
                sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
                shortened_text = ". ".join(sentences[:num_sentences])
                return shortened_text
            else:
                return "No information found on Wikipedia."
        else:
            return "No information found on Wikipedia."
    except requests.exceptions.HTTPError:
        return "Failed to retrieve information from Wikipedia."
    except requests.exceptions.RequestException:
        return "Error occurred while retrieving information from Wikipedia."


def remove_punctuation(sentence):
    # Remove punctuation marks
    sentence = sentence.translate(str.maketrans("", "", string.punctuation))
    return sentence

def extract_person_names_2(message):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(message)

    names = []
    for entity in doc.ents:
        if entity.label_ == 'PERSON':
            names.append(entity.text)

    if len(names) > 1:
        return names
    elif len(names) == 1:
        return '1'
    else:
        return False
    
# Following 2 functions works for 'Suggested Friends' Concept:
def find_suggested_friends(node, node_id):
    with driver.session() as session:
        result = session.run(
    "MATCH (n)<-[:has_IP_Address]-(friend:User) "
    "WHERE id(n) = $node_id "
    "RETURN friend.full_name AS suggested_friend",
    node_id=node_id
  )
        print('find_suggested_friends is activated.......................')
        suggested_friends = [record["suggested_friend"] for record in result]

    if suggested_friends:
        print('if in find_suggested_friends is activated.......................')
        suggested_friends.remove(get_current_user_name)
        bot_response = 'You may know ' + ', '.join(suggested_friends) + '. You must look for these people around you, ' + get_current_user_name + '.'
        return bot_response
    else:
        bot_response = 'Uh-oh! I cannot provide you with any friends suggestion becuase I do not know anyone around you.'
        return bot_response
        

# Function to search for a relationship by username
def check_relationship_in_neo4j(username):
    # Create a session
    print('check_relationship_in_neo4j is activated.......................')
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User {full_name: $username})-[:has_IP_Address]->(ip:User {full_name: 'IP Address'}) "
            "RETURN ip "
            "ORDER BY ip.username "
            "LIMIT 1",
            username=username
        )
        print('session.run has been done.......................')
        nodes = list(result.graph().nodes)
        print('Length of the nodes list is:', len(nodes))
        print('Line 445 running.......................')
        node = nodes[0]
        node_id = node.id  # New variable to store the 'id' of the node
        print('Node ID:', node_id)

    if nodes:
        print('if nodes activated.......................')
        node = nodes[0]
        #bot_response = f"The node with username '{username}' has a 'has_IP_Address' relationship with the node 'IP Address'."
        bot_response = find_suggested_friends(node, node_id)
        return bot_response
    else:
        bot_response = f"The node with username '{username}' does not have the expected relationship."
        return bot_response


def set_master():
    mybot.respond('Master is Louis', "Louis")

mute_words = ['prolog','pants', 't-shirt', 'boots', 'shoes', 'shirt', 'im', 'master','query','great', 'fine', 'well', 'What is','yes','who is','yeah','logo',"I'm",'hello', 'hey', 'hi', 'hola', 'amigo', 'greetings', 'what', 'tell', '?', 'am I', 'who', 'when', 'why']

def getresponse(request):
    set_master()
    user_message = request.GET.get('msg')
    tokens = list(word_tokenize(user_message))
    persons_exists = extract_person_names(user_message)
    if persons_exists == False:
        persons_exists = extract_person_names_2(user_message)
    target = ' IP'
    target2 = 'DATE'
    target3 = 'WIKIPEDIA'
    suggest_friends = 'SUGGEST ME FRIENDS'
    prefix1 = 'Fact is: '
    prefix2 = 'Query is: '
    
    if user_message.startswith(prefix1):
        new_fact = user_message[len(prefix1):]
        if new_fact:
            with open(r'pytholog_kb.pl', 'a') as file:
                file.write('\n' + new_fact)
            bot_response = 'New fact added! Thanks for letting me know, ' + get_current_user_name + '.'
            return HttpResponse(bot_response, content_type='text/plain')
    
    if user_message.startswith(prefix2):
        new_query = user_message[len(prefix2):]
        with open(r'pytholog_kb.pl', 'r') as file:
            knowledge = file.readlines()
        knowledge = [item.strip() for itSem in knowledge]
        kb(knowledge)
        result = kb.query(pl.Expr(new_query))
        bot_response = ' '.join(map(str, result))
        return HttpResponse(bot_response, content_type='text/plain')
        
    if target2.lower() in user_message:
        bot_response = getDate()
        return HttpResponse(bot_response, content_type='text/plain')
    if target3.lower() in user_message:
        query = user_message.replace('what does wikipedia says about', '').strip()
        bot_response = get_from_wikipedia(query)
        return HttpResponse(bot_response, content_type='text/plain')
    for word in target_words:
        if word in user_message and user_message != 'tell me my name':
            bot_response = process_input(user_message)
            if bot_response == 'sorry':
                break
            return HttpResponse(bot_response, content_type='text/plain')
    if target.lower() in user_message:
        bot_response = getIP()
        return HttpResponse(bot_response, content_type='text/plain') 
    if suggest_friends.lower() in user_message:
        #call search node in neo4j (username), it'll return the node of logged in person
        print('suggest_friends.lower() is activated....................')
        print('Current username sent to functions is:', get_current_user_name)
        bot_response = check_relationship_in_neo4j(get_current_user_name)
        return HttpResponse(bot_response, content_type='text/plain')
    #requires input as: 'Do you know that p1 is a friend of p2'
    if 'a friend of' in user_message:
        if persons_exists:
            user_message = remove_punctuation(user_message)
            tokens = user_message.split()
            person1 = tokens[4]
            middle_tokens = tokens[6:9]
            person2 = tokens[-1]
            
            person1_exists = search_person(person1)
            person2_exists = search_person(person2)
            if person1_exists and person2_exists:
                #print('Both persons are found!')
                bot_response = 'Oh I did not know that! Thanks for letting me know Anns!'
                joined_string = '_'.join(middle_tokens)
                relationship = str(joined_string.upper())
                #print(f'Relationship should be: {relationship}')
                create_relationship(person1, person2, relationship)
                return HttpResponse(bot_response, content_type='text/plain')
            else:
                bot_response = 'I guess I do not know about any one of them or maybe both, Can you tell him/her to sign up with me so I can catch your mate?'
                return HttpResponse(bot_response, content_type='text/plain')
        else:
            bot_response = 'I cannot detect two persons in your text buddy :/'
            return HttpResponse(bot_response, content_type='text/plain')
            
    else:
        bot_response = mybot.respond(user_message, "Louis")
        if bot_response:
            print('LouBot found a reposne in AIML!')
            return HttpResponse(bot_response, content_type='text/plain')
        else:
            print('LouBot is UNABLE to find a reposne in AIML!')
            if user_message != 'yeah' or user_message != 'Yeah':
                tags_list = create_tags(user_message)
                for word in mute_words:
                    if word in user_message or word.lower() in user_message or word.upper() in user_message:
                        terminate_storing_in_brain = True
                        print('terminate_storing_in_brain is set to True')
                        break
                    else:
                        terminate_storing_in_brain = False
                        print('terminate_storing_in_brain is set to False')
                for tag in tags_list:
                    print('Line 409 is active!')
                    if tag[1] == 'NNP' or tag[1] == 'NN' or tag[1] == 'NNS' or tag[0] == 'I':
                        print('Line 413 is active!')
                        if terminate_storing_in_brain == False:
                            print('Line 415 is active!')
                            if 'I' in user_message:
                                print('Line 412 is active!')
                                replaced_string = user_message.replace('I', get_current_user_name)
                                if 'you' in user_message:
                                    replaced_string = user_message.replace('you', 'LouBot')
                                print('Algorith detected a specific possession keywords and has automatically change it with current user name to learn efficiently.')
                                print('New User message:', replaced_string)
                                Semantics_for_Logged_In_Person(replaced_string)
                            else:
                                print('Line 417 is active!')
                                Semantics(user_message)
                                print('Line 420 is active!')
                        
            
            
