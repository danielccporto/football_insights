from football_stats.competitions import get_competitions, get_matches
from football_stats.matches import get_lineups, get_events, get_player_stats
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.schema import AIMessage, HumanMessage

from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from tools.football import get_sport_specialist_comments_about_match as comments_about_a_match
from tools.football import generate_match_summary, get_player_profile_tool
from football_stats.matches import get_main_events, generate_narrative
from tools import load_tools
import json

from agent import load_agent

import streamlit as st

st.set_page_config(layout="wide",
                   page_title="Football Match Conversation App",
                   page_icon="⚽️")

msgs = StreamlitChatMessageHistory()


if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(messages=msgs, memory_key="chat_history", return_messages=True)

memory = st.session_state.memory

def memorize_message():
    user_input = st.session_state["user_input"]
    st.session_state["memory"].chat_memory.add_message(HumanMessage(content=user_input))
    
def load_competitions():
    """
    Simulates loading competitions from your function.
    Replace this with the actual call to fetch competitions.
    """
    return json.loads(get_competitions())

def load_matches(competition_id, season_id):
    """
    Simulates loading matches for a specific competition.
    Replace this with the actual call to fetch matches for a competition.
    """
    return  json.loads(get_matches(competition_id, season_id))


# Streamlit Sidebar
st.sidebar.title("Football Match Selector")
# Step 1: Select a Competition
selected_competition = None
selected_season = None
selected_match = None
match_id = None
match_details = None
specialist_comments = None

st.sidebar.header("Step 1: Select a Competition")
competitions = load_competitions()
competition_names = sorted(set([comp['competition_name'] for comp in competitions]))
selected_competition = st.sidebar.selectbox("Choose a Competition",
                                            competition_names)
if selected_competition:
    # Step 2: Select a Season
    st.sidebar.header("Step 2: Select a Season")
    seasons = set(comp['season_name'] for comp in competitions
                  if comp['competition_name'] == selected_competition)
    selected_season = st.sidebar.selectbox("Choose a Season", sorted(seasons))
    
    
if selected_season:
    # Get the selected competition ID
    competition_id = next(
        (comp['competition_id'] for comp in competitions 
         if comp['competition_name'] == selected_competition),
        None
    )
    season_id = next(
        (comp['season_id'] for comp in competitions 
                               if comp['season_name'] == selected_season 
                               and comp['competition_name'] == selected_competition),
        None
    )
    # Step 2: Select a Match
    st.sidebar.header("Step 3: Select a Match")
    matches = load_matches(competition_id, season_id)
    match_names = sorted([f"{match['home_team']} vs {match['away_team']}" for match in matches])
    
    if selected_match:=st.sidebar.selectbox("Choose a Match", match_names):
        # Get the selected match ID
        match_details = next(
            (match for match in matches if f"{match['home_team']} vs {match['away_team']}" == selected_match),
            None
        ) 
        match_id = match_details['match_id']
        
# Main Page
if not match_id:
    st.title("Football Match Conversation")
    st.write("Use the sidebar to select a competition, then a match, and start a conversation.")
else:
    st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True)
    st.markdown(f'<h1 class="title">{selected_match}</h1><h3 class="title">{selected_competition} - Season {selected_season}</h3>', unsafe_allow_html=True)
    with st.container(border=False):
        st.chat_input(key="user_input", on_submit=memorize_message) 
        if user_input := st.session_state.user_input:
            chat_history = st.session_state["memory"].chat_memory.messages
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.write(f"{msg.content}")
                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.write(f"{msg.content}")
                        
            with st.spinner("Agent is responding..."):
                try:
                    # Load agent
                    agent = load_agent()
                    
                    # Cache tools to avoid redundant calls
                    tools = load_tools()
                    tool_names = [tool.name for tool in tools]
                    tool_descriptions = [tool.description for tool in tools]

                    # Prepare input for the agent
                    input_data = {
                        "match_id": match_id,
                        "match_name": selected_match,
                        "input": user_input,
                        "agent_scratchpad": "",
                        "competition_id": competition_id,
                        "season_id": season_id,
                        "tool_names": tool_names,
                        "tools": tool_descriptions,
                    }

                    # Debug: Print input to verify structure (optional)
                    # st.write(f"Input to agent: {input_data}")

                    # Invoke agent
                    response = agent.invoke(input=input_data, handle_parsing_errors=True)

                    # Validate response
                    if isinstance(response, dict) and "output" in response:
                        output = response.get("output")
                    else:
                        output = "Sorry, I couldn't understand your request. Please try again."

                    # Add response to chat memory
                    st.session_state["memory"].chat_memory.add_message(AIMessage(content=output))

                    # Display response in chat
                    with st.chat_message("assistant"):
                        st.write(output)

                except Exception as e:
                    # Handle and display errors gracefully
                    st.error(f"Error during agent execution: {str(e)}")
                    st.write("Ensure that your inputs and agent configuration are correct.")


# Match Summary Section
st.header("Match Summary")
with st.spinner("Generating match summary..."):
    match_summary = generate_match_summary(
        match_id=match_id,
        match_details={
            "home_team": match_details['home_team'],
            "away_team": match_details['away_team'],
            "competition": selected_competition,
            "season": selected_season,
            "score": f"{match_details.get('home_score', 'N/A')} - {match_details.get('away_score', 'N/A')}"
        }
    )
    st.write(match_summary)

if match_id:
    st.sidebar.header("Player Profile")
    player_name = st.sidebar.text_input("Enter the Player's Name")

    if st.sidebar.button("Get Player Profile"):
        with st.spinner("Retrieving player profile..."):
            # Chama a ferramenta para gerar o perfil do jogador
            action_input = json.dumps({"match_id": match_id, "player_name": player_name})
            player_profile = get_player_profile_tool(action_input)
            
            # Exibe o perfil do jogador
            st.subheader(f"Player Profile: {player_name}")
            st.json(player_profile)


# Sidebar para seleção de estilo
st.sidebar.title("Narrative Generator")
st.sidebar.header("Select Match and Style")

# Input para seleção de Match ID
match_id = st.sidebar.number_input("Enter the Match ID", value=0, step=1, format="%d")

# Input para seleção de estilo
style = st.sidebar.selectbox(
    "Choose Narrative Style",
    ["formal", "humoristic", "technical"]
)

# Botão para gerar narrativa
if st.sidebar.button("Generate Narrative"):
    if match_id == 0:
        st.error("Please enter a valid Match ID.")
    else:
        try:
            # Obter eventos da partida
            events_json = get_main_events(match_id)
            events = json.loads(events_json)
            
            # Gerar narrativa
            narrative_json = generate_narrative(events=events, style=style)
            narrative = json.loads(narrative_json)

            # Exibir resultado
            st.subheader("Narrative Result")
            st.write(narrative['narrative'])
        
        except Exception as e:
            st.error(f"Error generating narrative: {e}")
