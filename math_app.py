import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import LLMMathChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents import Tool
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain import hub
import os

# Custom CSS for dark theme with glowing effects
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Exo+2:wght@300;400;500;600&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Exo 2', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Header styling with glow */
    .main-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffff, #0077ff, #7700ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.7),
                     0 0 40px rgba(0, 119, 255, 0.5),
                     0 0 60px rgba(119, 0, 255, 0.3);
        margin-bottom: 0.5rem;
        padding: 1rem;
        animation: glow-pulse 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow-pulse {
        from {
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.7),
                         0 0 40px rgba(0, 119, 255, 0.5),
                         0 0 60px rgba(119, 0, 255, 0.3);
        }
        to {
            text-shadow: 0 0 25px rgba(0, 255, 255, 0.9),
                         0 0 50px rgba(0, 119, 255, 0.7),
                         0 0 75px rgba(119, 0, 255, 0.5);
        }
    }
    
    /* Subheader styling */
    .sub-header {
        font-family: 'Exo 2', sans-serif;
        font-size: 1.2rem;
        text-align: center;
        color: #a0a0e0;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Chat container styling */
    .chat-container {
        background: rgba(15, 25, 45, 0.8);
        border-radius: 20px;
        border: 1px solid rgba(0, 255, 255, 0.3);
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
        max-height: 70vh;
        overflow-y: auto;
    }
    
    /* Message styling */
    .message {
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 18px;
        font-family: 'Exo 2', sans-serif;
        line-height: 1.6;
        animation: fadeIn 0.5s ease-in;
        max-width: 85%;
        word-wrap: break-word;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* User message styling */
    .user-message {
        background: linear-gradient(135deg, #0077ff, #00aaff);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
        box-shadow: 0 4px 15px rgba(0, 119, 255, 0.4);
        border: 1px solid rgba(0, 200, 255, 0.5);
    }
    
    /* Assistant message styling */
    .assistant-message {
        background: rgba(30, 35, 60, 0.9);
        color: #e0e0ff;
        margin-right: auto;
        border-bottom-left-radius: 5px;
        border: 1px solid rgba(150, 0, 255, 0.4);
        box-shadow: 0 4px 15px rgba(100, 0, 255, 0.3);
    }
    
    /* Message header styling */
    .message-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .user-header {
        color: #80fffd;
        justify-content: flex-end;
    }
    
    .assistant-header {
        color: #c080ff;
        justify-content: flex-start;
    }
    
    /* Input area styling */
    .input-container {
        background: rgba(15, 25, 45, 0.9);
        border: 1px solid rgba(0, 255, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
    }
    
    /* Button styling with glow effect */
    .stButton button {
        font-family: 'Exo 2', sans-serif;
        font-weight: 600;
        background: linear-gradient(90deg, #00aaff, #0077ff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0, 170, 255, 0.5);
        position: relative;
        overflow: hidden;
        width: 100%;
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, #0077ff, #00aaff);
        box-shadow: 0 0 25px rgba(0, 170, 255, 0.8),
                    0 0 35px rgba(0, 170, 255, 0.6);
        transform: translateY(-2px);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background: rgba(20, 30, 50, 0.9);
        border: 1px solid rgba(0, 200, 255, 0.3);
        border-radius: 12px;
        color: #ffffff;
        font-family: 'Exo 2', sans-serif;
        font-size: 1rem;
        padding: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 200, 255, 0.2);
        resize: vertical;
        min-height: 100px;
    }
    
    .stTextArea textarea:focus {
        border-color: #00ffff;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
        outline: none;
    }
    
    /* Success message styling */
    .stSuccess {
        background: rgba(0, 150, 100, 0.2);
        border: 1px solid rgba(0, 255, 200, 0.4);
        border-radius: 12px;
        color: #70ffd0;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 0 15px rgba(0, 255, 200, 0.3);
    }
    
    /* Warning message styling */
    .stWarning {
        background: rgba(200, 150, 0, 0.2);
        border: 1px solid rgba(255, 200, 0, 0.4);
        border-radius: 12px;
        color: #ffd870;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 0 15px rgba(255, 200, 0, 0.3);
    }
    
    /* Custom Loading Animation */
    .neuro-loader {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: rgba(20, 30, 50, 0.8);
        border-radius: 15px;
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
        margin: 1rem 0;
    }
    
    .loader-brain {
        font-size: 3rem;
        margin-bottom: 1rem;
        animation: brain-pulse 2s ease-in-out infinite;
    }
    
    @keyframes brain-pulse {
        0%, 100% { 
            transform: scale(1);
            filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.7));
        }
        50% { 
            transform: scale(1.1);
            filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.9));
        }
    }
    
    .loader-text {
        font-family: 'Exo 2', sans-serif;
        font-size: 1.1rem;
        color: #00ffff;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .loader-dots {
        display: flex;
        gap: 0.5rem;
    }
    
    .dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: linear-gradient(45deg, #00ffff, #0077ff);
        animation: dot-bounce 1.4s ease-in-out infinite both;
    }
    
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }
    .dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes dot-bounce {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
    
    .loader-progress {
        width: 100%;
        height: 4px;
        background: rgba(0, 255, 255, 0.2);
        border-radius: 2px;
        margin-top: 1rem;
        overflow: hidden;
    }
    
    .loader-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #00ffff, #0077ff);
        border-radius: 2px;
        animation: progress-shimmer 2s ease-in-out infinite;
        width: 45%;
    }
    
    @keyframes progress-shimmer {
        0% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
        100% { transform: translateX(200%); }
    }
    
    /* Thinking process animation */
    .thinking-process {
        background: rgba(30, 35, 60, 0.9);
        border: 1px solid rgba(150, 0, 255, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: thinking-glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes thinking-glow {
        from {
            box-shadow: 0 0 10px rgba(150, 0, 255, 0.3);
        }
        to {
            box-shadow: 0 0 20px rgba(150, 0, 255, 0.6);
        }
    }
    
    .thinking-text {
        font-family: 'Exo 2', sans-serif;
        color: #c080ff;
        font-size: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .thinking-icons {
        display: flex;
        justify-content: center;
        gap: 1rem;
        font-size: 1.5rem;
        animation: thinking-float 3s ease-in-out infinite;
    }
    
    @keyframes thinking-float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    
    /* Header icons container */
    .header-icons {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1rem 0 2rem 0;
        font-size: 2.5rem;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(20, 25, 45, 0.7);
        border: 1px solid rgba(0, 200, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: rgba(0, 255, 255, 0.5);
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.3);
        transform: translateY(-5px);
    }
    
    /* Clear chat button */
    .clear-btn {
        background: linear-gradient(90deg, #ff6b6b, #ff8e8e) !important;
        box-shadow: 0 0 15px rgba(255, 107, 107, 0.5) !important;
    }
    
    .clear-btn:hover {
        background: linear-gradient(90deg, #ff8e8e, #ff6b6b) !important;
        box-shadow: 0 0 25px rgba(255, 107, 107, 0.8) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .header-icons {
            font-size: 2rem;
            gap: 1rem;
        }
        
        .feature-card {
            padding: 1rem;
        }
        
        .message {
            max-width: 95%;
        }
        
        .chat-container {
            padding: 1rem;
            max-height: 60vh;
        }
        
        .loader-brain {
            font-size: 2.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

## Set up the Streamlit app
st.set_page_config(
    page_title="Syam's NeuroMath AI - Advanced Mathematical Intelligence",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Header with icons and title
st.markdown('<div class="header-icons">🚀 ✨ 🤖 ⚡ 📊</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">Syam\'s NeuroMath AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced Mathematical Intelligence • Real-time Computation • AI-Powered Reasoning</p>', unsafe_allow_html=True)

from dotenv import load_dotenv
load_dotenv()

# Get Groq API Key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.info("🔑 Please add your Groq API Key to continue")
    st.stop()

llm = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

## Initializing the tools
wikipedia_wrapper = WikipediaAPIWrapper()
wikipedia_tool = Tool(
    name="Wikipedia",
    func=wikipedia_wrapper.run,
    description="A tool for searching the Internet to find the various information on the topics mentioned"
)

## Initializing the Math tool
math_chain = LLMMathChain.from_llm(llm=llm)

def calculator_func(question):
    """Function to handle math calculations"""
    return math_chain.invoke({"question": question})

calculator = Tool(
    name="Calculator",
    func=calculator_func,
    description="A tools for answering math related questions. Only input mathematical expression need to be provided"
) 

prompt = """
Your a agent tasked for solving users mathematical question. Logically arrive at the solution and provide a detailed explanation
and display it point wise for the question below
Question:{question}
Answer:
"""

prompt_template = PromptTemplate(
    input_variables=["question"],
    template=prompt
)

## Create a reasoning chain using modern pattern
reasoning_chain = prompt_template | llm

def reasoning_func(question):
    """Function to handle reasoning questions"""
    return reasoning_chain.invoke({"question": question})

reasoning_tool = Tool(
    name="Reasoning tool",
    func=reasoning_func,
    description="A tool for answering complex questions that require reasoning and explanation."
)

## initialize the modern agent
# Get the react prompt from hub
react_prompt = hub.pull("hwchase17/react")

# Create the react agent
agent = create_react_agent(llm, [wikipedia_tool, calculator, reasoning_tool], react_prompt)

# Create agent executor
assistant_agent = AgentExecutor(agent=agent, tools=[wikipedia_tool, calculator, reasoning_tool], verbose=True)

# Feature cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00ffff; margin-bottom: 1rem;">🧮 Mathematical Solver</h3>
        <p style="color: #a0a0e0; font-size: 0.9rem;">Advanced computational engine for complex mathematical problems with step-by-step solutions.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #7700ff; margin-bottom: 1rem;">🔍 Data Intelligence</h3>
        <p style="color: #a0a0e0; font-size: 0.9rem;">Real-time data search and analysis powered by Wikipedia integration and AI reasoning.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00ffaa; margin-bottom: 1rem;">⚡ Lightning Fast</h3>
        <p style="color: #a0a0e0; font-size: 0.9rem;">Powered by Groq's ultra-fast inference engine for instant responses and calculations.</p>
    </div>
    """, unsafe_allow_html=True)

# Chat interface
st.markdown("---")
st.markdown("### 💬 Chat with Syam's NeuroMath AI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🌟 Welcome to Syam's NeuroMath AI! I can help you solve complex mathematical problems, search for information, and provide detailed explanations with step-by-step reasoning. How can I assist you today?"}
    ]

# Chat container
with st.container():
   
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f"""
                <div class="message user-message">
                    <div class="message-header user-header">
                        👤 You
                    </div>
                    {message["content"]}
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="message assistant-message">
                    <div class="message-header assistant-header">
                        🤖 Syam's NeuroMath AI
                    </div>
                    {message["content"]}
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Input area

col1, col2 = st.columns([3, 1])

with col1:
    user_input = st.text_area(
        " ",
        placeholder="Enter your mathematical problem or question here...",
        height=100,
        key="user_input",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    send_button = st.button("Send", use_container_width=True)
    clear_button = st.button("Clear", use_container_width=True, type="secondary")

st.markdown('</div>', unsafe_allow_html=True)

# Handle clear chat
if clear_button:
    st.session_state.messages = [
        {"role": "assistant", "content": "🌟 Chat cleared! How can I help you with mathematical problems or data analysis today?"}
    ]
    st.rerun()

# Handle user input
if send_button and user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate assistant response with custom loading animation
    with st.container():
        st.markdown("""
        <div class="neuro-loader">
            <div class="loader-brain">🧠</div>
            <div class="loader-text">NeuroMath AI is processing your query</div>
            <div class="loader-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="loader-progress">
                <div class="loader-progress-bar"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Thinking process animation
        st.markdown("""
        <div class="thinking-process">
            <div class="thinking-text">Analyzing mathematical patterns and reasoning step-by-step...</div>
            <div class="thinking-icons">
                <span>🔢</span>
                <span>📊</span>
                <span>🧮</span>
                <span>⚡</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            response = assistant_agent.invoke({"input": user_input})
            # Extract the output from the response
            output = response.get("output", str(response))
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            error_msg = f"⚠️ I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or ask something else."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem; padding: 2rem;">'
    'Powered by Groq • Gemini 2 • LangChain • Streamlit<br>'
    'Syam\'s NeuroMath AI © 2024 | Advanced Mathematical Intelligence System'
    '</div>',
    unsafe_allow_html=True
)

