# Football Insights

## **Project Description**
**Football Insights** is an interactive football match analysis application that combines data retrieval, AI-driven insights, and an engaging user interface. It uses **Streamlit** for the frontend, **LangChain** for agent-based reasoning with Google Gemini Pro, and **StatsBombPy** for accessing comprehensive football data, including matches, events, and player statistics.

The primary goal of the project is to allow users to:
- Select competitions, seasons, and matches.
- Retrieve match details, starting XI, and player statistics.
- Receive AI-generated insights and commentary on matches.

---

## **Project Structure**
```
Football Insights (at_datadriven)
|
|-- football_app/
|   |-- src/football_app/
|       |-- __init__.py
|       |-- app.py            # Main Streamlit application
|       |-- agent.py          # Agent configuration using LangChain
|       |-- tools/            # Tools for match details, comments, and external search
|           |-- __init__.py
|           |-- football.py   # Functions for analysis and specialist comments
|           |-- self_ask_agent.py  # Self-ask agent with GoogleSerperAPIWrapper
|       |-- football_stats/   # Match and competition statistics
|           |-- __init__.py
|           |-- competitions.py   # Fetch competitions and matches
|           |-- matches.py        # Retrieve events, lineups, and player stats
|
|-- venv/                      # Virtual environment
|-- requirements.txt           # Project dependencies
|-- .env                       # API keys and environment variables
|-- README.md                  # Documentation
```

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/your_username/football_insights.git
cd football_insights/football_app
```

### **2. Set Up a Virtual Environment**
Create and activate a Python virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### **3. Install Dependencies**
Install the required libraries:
```bash
pip install -r requirements.txt
```

### **4. Configure Environment Variables**
Create a `.env` file in the project root directory and include your **SERPER_API_KEY**:
```
SERPER_API_KEY=your_serper_api_key
```

### **5. Run the Application**
To start the **Streamlit** interface:
```bash
streamlit run src/football_app/app.py
```
The application will be available at `http://localhost:8501`.

---

## **Features and Functionality**

### **1. Select Competitions and Matches**
- **Input**: Select a competition and season, then choose a specific match.
- **Output**: Match details such as teams, players, and events.

### **2. Chat Interaction with AI Agent**
- **Input**: User query related to the match (e.g., "Who were the key players?").
- **Output**: AI-generated insights and analysis, leveraging match data.

### **3. Specialist Commentary**
- **Input**: Automatically processes match details and lineups.
- **Output**: A sports commentator-like analysis using AI.

---

## **Example**

### **Input (User Chat):**
> "Tell me about the starting XI for both teams in the selected match."

### **Output (AI Response):**
> "Hello everyone! The match between **Team A** and **Team B** featured a strong lineup. For **Team A**, Player X played as a striker, leading the attack..."

---

Enjoy using Football Insights! ⚽🚀

