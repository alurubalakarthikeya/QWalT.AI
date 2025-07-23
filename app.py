import streamlit as st

st.set_page_config(page_title="QWalT.AI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
body {
    background-color: white;
}
header[data-testid="stHeader"] {
    background-color: transparent;
}
.main {
    padding-top: 0rem;
    height: 100vh;
}
.top-banner {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #172d43;
    color: #91baf2;
    font-weight: bold;
    font-size: 1.6rem;
    padding: 1.2rem;
    z-index: 999;
}

.chat-container {
    height: calc(100vh - 9rem);
    position: fixed;
    bottom: 4.5rem;
}

.chat-bubble {
    padding: 1rem 1.3rem;
    border-radius: 1rem;
    margin: 0.4rem 0;
    max-width: 85%;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.user-msg {
    background-color: #172d43;
    color: white;
    margin-left: auto;
    text-align: right;
    width: fit-content;
}
.bot-msg {
    background-color: #91baf2;
    color: white;
    margin-right: auto;
    text-align: left;
    width: fit-content;
}
.input-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #f5f5f5;
    padding: 1rem;
    z-index: 100;
}
.stTextInput > div > input {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 70%;
    padding: 0.75rem 1rem;
    font-size: 16px;
    border-radius: 1rem;
    border: 1px solid #ccc;
}
div.stButton > button {
    background-color: #6A0DAD; /* Purple */
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover {
    background-color: #4B0082; /* Darker purple */
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="top-banner">QWalT.AI</div>', unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.info("""
**🤖 Welcome!**  
I'm your AI assistant bot — here to help you with anything from simple questions to complex problems. Go ahead and type your query below!
""")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for entry in st.session_state.chat_history:
    st.markdown(f'<div class="chat-bubble user-msg">You: {entry["user"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chat-bubble bot-msg">QWalT.AI: {entry["bot"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Fixed Input Area
st.markdown('<div class="input-fixed">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    col1, col2 = st.columns([9, 1])
    with col1:
        user_input = st.text_input("", placeholder="Ask something...", label_visibility="collapsed")
    with col2:
        submitted = st.form_submit_button("Send")
        if submitted and user_input:
            response = f"This is a placeholder response for: '{user_input}'"
            st.session_state.chat_history.append({"user": user_input, "bot": response})
            st.experimental_rerun()
st.markdown('</div>', unsafe_allow_html=True)
