# Graph-Augmented Conversational Chatbot with Semantic Knowledge Retrieval

## Project Overview

This system implements a knowledge-augmented conversational agent that combines traditional rule-based dialogue (AIML), natural language processing, and graph-based semantic memory. The architecture leverages Neo4j as a persistent knowledge graph to model entities, relationships, and contextual information extracted dynamically from user conversations. Unlike conventional chatbots that rely solely on pattern matching or transformer-based models, this system maintains a structured, queryable representation of conversational knowledge that evolves over time.

## Motivation & Design Rationale

### Why Graph Databases?

Relational databases model data as tables with fixed schemas, optimized for transactional queries over normalized structures. However, conversational knowledge is inherently relational and hierarchical—entities are connected through multi-hop relationships that are expensive to traverse in SQL (multiple JOINs, recursive CTEs).

Neo4j was chosen for the following technical reasons:

1. **Native Graph Traversal**: Relationships are first-class citizens, stored as direct pointers between nodes. Queries like "find friends of friends with shared IP addresses" execute in constant time per relationship, not dependent on table size.

2. **Schema Flexibility**: Conversational knowledge is semi-structured. New entity types and relationship types emerge dynamically as users interact. Graph databases support property graphs where nodes and edges can have arbitrary key-value properties without schema migrations.

3. **Pattern Matching with Cypher**: Cypher's declarative query language is optimized for path-based queries. The system uses MATCH clauses to traverse multi-hop relationships (e.g., user → IP address → co-located users) for features like friend recommendations.

4. **Knowledge Representation**: The system models a social-semantic network where users, entities extracted from text, and contextual metadata (IP addresses, timestamps) form a heterogeneous graph. This enables reasoning over indirect relationships.

## System Architecture

The architecture consists of four primary layers:

```
┌─────────────────────────────────────────────────────────┐
│  Django Web Layer (views.py, templates)                 │
│  - User authentication, session management               │
│  - HTTP endpoints for chat interface                     │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Dialogue Management & NLP Pipeline                      │
│  - AIML pattern matching (100+ .aiml files)             │
│  - NER (spaCy, NLTK) for entity extraction              │
│  - POS tagging for semantic role labeling               │
│  - WordNet integration for definitions                  │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Knowledge Storage & Reasoning Layer                     │
│  ├─ Neo4j Graph Database (semantic memory)              │
│  ├─ Pytholog Knowledge Base (logical inference)         │
│  └─ AIML Brain (serialized pattern state)               │
└─────────────────────────────────────────────────────────┘
```

### Request Flow

1. User input arrives at `/get/` endpoint
2. AIML kernel attempts pattern match
3. If no match, NLP pipeline activates:
   - POS tagging extracts nouns (entities) and verbs (relations)
   - Named Entity Recognition identifies persons, locations
   - Entities and relationships stored in Neo4j as `(User)-[RELATION]->(Entity)` triples
4. Neo4j Cypher queries retrieve contextual knowledge
5. Response generation combines retrieval, inference, and rule-based templates

## Graph Data Model (Neo4j)

### Node Types

| Label      | Properties                                   | Purpose                                      |
|------------|----------------------------------------------|----------------------------------------------|
| `User`     | `full_name`, `username`, `email`, `password` | Authenticated system users                    |
| `User`     | `name`                                       | General entities extracted from conversations |
| `Person`   | `name`                                       | Named persons mentioned by logged-in users    |
| `User`     | `full_name: "IP Address"`, `ip_address`      | IP address nodes for network-based inference  |

**Design note**: The system overloads the `User` label for both authenticated users and extracted entities. This simplifies queries but sacrifices semantic clarity. A production system would use distinct labels (`Account`, `Entity`, `IPNode`).

### Relationship Types

Relationships are dynamically generated from parsed sentence structure:

- **Static relationships**:
  - `(User)-[:has_IP_Address]->(User {full_name: "IP Address"})`: Links users to their IP addresses for geo-proximity inference

- **Dynamic relationships**:
  - Extracted from POS-tagged verbs, e.g., `"John loves pizza"` → `(John)-[:LOVES]->(pizza)`
  - Relationship names are constructed by joining intermediate tokens with underscores, then uppercasing

### Query Patterns

#### User Authentication
```cypher
MATCH (u:User) 
WHERE u.username = $username AND u.password = $password 
RETURN COUNT(u) AS count
```

#### Friend Suggestion (Shared Network)
```cypher
MATCH (n)<-[:has_IP_Address]-(friend:User)
WHERE id(n) = $node_id
RETURN friend.full_name AS suggested_friend
```
This traverses the graph to find users sharing the same IP address node, implementing proximity-based social recommendations.

#### Semantic Triple Storage
```cypher
MATCH (n:User {name: $entity1}), (m:User {name: $entity2})
MERGE (n)-[r:DYNAMIC_RELATION]->(m)
```
New relationships are created as `MERGE` operations, avoiding duplicates.

### Graph Traversal Workflow

1. **Entity grounding**: Extracted entities are matched against existing nodes via `full_name` or `name` properties
2. **Relationship creation**: If entities exist, a directed edge is created with the relationship type derived from the verb phrase
3. **Contextual linking**: User-specific knowledge links to the authenticated user's node via `full_name`

## Knowledge-Driven Workflow

### Semantic Memory Construction

When the chatbot encounters an unfamiliar sentence:

1. **Tokenization & Tagging**: `word_tokenize` → `pos_tag` → extract nouns (NNP, NN, NNS) and verbs (VBZ, VBP, VB)
2. **Graph Write**: 
   - For general statements: Create two `User` nodes and a relationship
   - For first-person statements: Link to the logged-in user's node via `Semantics_for_Logged_In_Person()`
3. **Pronoun Resolution**: "I" is replaced with the user's `full_name`, "you" with "LouBot"

### Hybrid Reasoning

The system integrates three reasoning paradigms:

1. **Pattern-Based (AIML)**: Fast, deterministic responses for common queries
2. **Graph-Based (Neo4j)**: Traversal queries for relational knowledge (e.g., "Who are my friends?")
3. **Logic-Based (Pytholog)**: Prolog-style inference for rules like `father(X, Y) :- male(X), parent(X, Y)`

### External Knowledge Integration

- **WordNet**: On-demand word definitions via synset lookup
- **Wikipedia**: Scrapes and summarizes Wikipedia articles using BeautifulSoup when queries match pattern `"what does wikipedia say about X"`

## Tech Stack

| Component       | Technology          | Purpose                                |
|-----------------|---------------------|----------------------------------------|
| Web Framework   | Django 4.2          | HTTP routing, session management       |
| Graph Database  | Neo4j (Bolt)        | Semantic knowledge graph               |
| NLP             | spaCy, NLTK         | NER, POS tagging, tokenization         |
| Dialogue Engine | PyAIML              | Rule-based pattern matching            |
| Logic Engine    | Pytholog            | Prolog-style inference                 |
| Graph Driver    | neo4j-driver, py2neo| Cypher query execution                 |
| Frontend        | HTML/CSS/JS         | Chat interface (static assets)         |

## Setup & Installation

### Prerequisites

- Python 3.8+
- Neo4j 4.0+ (local instance or Docker)
- Virtual environment (recommended)

### Installation Steps

```bash
# Clone repository
git clone <repository-url>
cd Graph-Augmented-Conversational-Chatbot-with-Semantic-Knowledge-Retrieval-main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install django python-aiml nltk spacy beautifulsoup4 py2neo neo4j pytholog

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words'); nltk.download('stopwords'); nltk.download('wordnet')"

# Start Neo4j
# Update connection credentials in app/views.py lines 32-34:
# uri = "bolt://localhost:7687"
# user = "neo4j"
# password = "your_password"

# Apply migrations
python manage.py migrate

# Run server
python manage.py runserver
```

Access the application at `http://localhost:8000`.

## Usage

### Basic Interaction
- Register a user via `/signup/`
- Login redirects to `/chatbox/`
- Chat interface sends AJAX requests to `/get/?msg=<user_message>`

### Knowledge Extraction

**Input**: `"Alice is a friend of Bob"`
- **System action**: Extracts entities `Alice`, `Bob`, verbs `is a friend of`, creates `(Alice)-[:IS_A_FRIEND_OF]->(Bob)`

**Input**: `"I love programming"`
- **System action**: Replaces "I" with logged-in user's name, creates `(UserName)-[:LOVE]->(programming)`

### Prolog Inference

**Input**: `"Fact is: male(john)"`
- Appends fact to `pytholog_kb.pl`

**Input**: `"Query is: father(john, X)"`
- Executes Prolog query against knowledge base

### Friend Suggestions

**Input**: `"Suggest me friends"`
- Queries Neo4j for users sharing the same IP address
- Returns: `"You may know Alice, Bob. You must look for these people around you."`

## Limitations & Assumptions

1. **No password hashing**: Passwords stored in plaintext (line 34, 160 in `views.py`)
2. **IP-based proximity**: Assumes users on the same local network are acquaintances
3. **Relationship extraction**: Heuristic POS-based parsing
4. **Graph schema**: Overloaded `User` label reduces query precision

## Future Improvements

### Short-Term
- Implement proper authentication (bcrypt/Argon2 hashing)
- Add entity linking (resolve synonyms, aliases)
- Enhance NER with contextual embeddings (BERT-based)
- Add graph visualization endpoint (D3.js or Cytoscape.js)

### Research Directions
- **Temporal reasoning**: Add timestamps to relationships for event ordering
- **Subgraph embeddings**: Train graph neural networks (GNNs) on Neo4j subgraphs for recommendation
- **Contradiction detection**: Use graph constraints to flag inconsistent facts
- **Multi-hop reasoning**: Implement attention-based path ranking for complex queries
- **Federated learning**: Privacy-preserving knowledge aggregation across user graphs

## License

Project by Anns Ijaz
