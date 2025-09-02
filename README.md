# AI Negotiation Agent 
An AI-powered buyer agent that negotiates prices with sellers using FastAPI for the backend and Ollama as the AI engine.  
This project enables real-time conversations, personalized buyer personas, and smart counteroffers to simulate human-like price negotiations.

# Features 

* AI-driven price negotiation powered by Ollama
* Context-aware responses based on product, budget, and previous messages
* Session-based conversations (persists negotiation history)
* Smart counteroffers with reasoning
* Simple and responsive web interface for testing the agent

# How It Works
 **User provides:**

* Product name
* Maximum budget
* Seller's offer

**AI Agent responds with:**

* Accept / Reject / Counteroffer
* Polite negotiation messages
* Justification for decisions
* Continue the conversation until deal is made!


# Tech Stack

| Component  | Technology   |
|------------|-------------|
| Backend    | FastAPI     |
| AI Agent   | ollama      |
| Frontend   | HTML/CSS/JS |
| Deployment | (Optional)  |


# Installing Ollama (Required)

Ollama is the AI engine powering the negotiation agent.

## Step 1 — Download Ollama

* Visit the Ollama Official Website
* Download the installer for your OS (Windows / macOS / Linux)
* Complete the installation process.

## Step 2 — Pull the AI Model
ollama pull llama3

## Step 3 — Run Ollama in the Background
ollama serve


# Installation 

### 1. Clone the repo
git clone https://github.com/sanjaiycs/Negotiation-Agent.git  
cd ai-negotiation-agent

### 2. Set up virtual environment
python -m venv .venv  
.\.venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the server
uvicorn app.main:app --reload

### 5. Open in browser
http://localhost:8000

# Screenshots

![image alt](https://github.com/sanjaiycs/Hackathon/blob/79eaf2af74cfbfec401335662fedb23f94bc8c93/Screenshot%202025-08-18%20at%207.43.39%20PM.jpg)

![image alt](https://github.com/sanjaiycs/Hackathon/blob/0306e19b17d3bfb3783152a134c1ec37aa315339/Screenshot%202025-08-18%20at%207.43.58%20PM.jpg)

# Future Improvements 

* Add more buyer personas
* Support multiple products
* Save negotiation history
* Deploy to cloud

