import streamlit as st
import requests
import uuid

st.set_page_config(page_title="MiaMigo")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessionId" not in st.session_state:
    st.session_state.sessionId = str(uuid.uuid4())

# Affichage de tout l'historique du chat AVANT le traitement du nouveau message
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input chat
prompt = st.chat_input("Votre message...")

if prompt:
    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Afficher le message utilisateur
    with st.chat_message("user"):
        st.write(prompt)
    
    # Traitement et affichage de la réponse
    with st.chat_message("assistant"):
        with st.spinner("Attente de la réponse..."):
            try:
                resp = requests.post(
    "http://n8n:5678/webhook/miamigo",
    json={"message": prompt, "sessionId": st.session_state.sessionId},
    timeout=300
)

                resp.raise_for_status()
                answer = resp.json()["output"]
            except Exception as e:
                answer = f"Erreur lors de l'appel : {e}"
            
            st.markdown(answer)
            # Ajouter la réponse à l'historique
            st.session_state.messages.append({"role": "assistant", "content": answer})

# Forcer le scroll vers le bas
st.markdown(
    """
    <script>
    window.parent.document.querySelector('section.main').scrollTo(0, window.parent.document.querySelector('section.main').scrollHeight);
    </script>
    """,
    unsafe_allow_html=True
)