import streamlit as st
import requests
import uuid
import psycopg2
import json

st.set_page_config(page_title="MiaMigo", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    if not st.user.is_logged_in:
        st.info("Veuillez vous connecter pour accéder au chat.")
        if st.button("🔑 Se connecter avec Google", type="primary", use_container_width=True):
            st.login("google")
    else:
        # --- Vérification / initialisation utilisateur ---
        try:
            conn = psycopg2.connect(
                dbname="miamigo",
                user="n8n",
                password="n8npass", #TODO
                # password="coolraoul",
                host="postgres",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM liste WHERE user_mail = %s;", (st.user.email,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(
                    """
                    INSERT INTO liste (user_mail, titres_recette, urls, articles)
                    VALUES (%s, ARRAY[]::text[], ARRAY[]::text[], '{}'::jsonb);
                    """,
                    (st.user.email,)
                )
                conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Erreur lors de l'initialisation de votre compte : {e}")

        # --- Informations utilisateur ---
        a, b = st.columns([1, 3])
        with a:
            st.image(st.user.picture, width=50, output_format="PNG")
            st.markdown(
                """
                <style>
                [data-testid="stImage"] img {
                    border-radius: 50%;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
        with b:
            st.write(f"Bienvenue {st.user.name}!")
        st.divider()

        # --- Boutons avec st.dialog ---
        @st.dialog("🧾 Ma liste de courses", width="large")
        def show_liste():
            try:
                conn = psycopg2.connect(
                    dbname="miamigo",
                    user="postgres",
                    password="coolraoul",
                    host="postgres",
                    port="5432"
                )
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT titres_recette, urls, articles
                    FROM liste
                    WHERE user_mail = %s;
                    """,
                    (st.user.email,)
                )
                result = cur.fetchone()

                if not result:
                    st.info("Vous n'avez pas encore de liste enregistrée.")
                    st.button("➕ Créer une liste vide", disabled=True)
                    return

                titres_recette, urls, articles_json = result

                # --- Recettes ---
                st.subheader("📖 Mes recettes")
                if not titres_recette:
                    st.write("Aucune recette dans votre liste.")
                else:
                    for titre, url in zip(titres_recette, urls):
                        st.markdown(f"- [{titre}]({url})")

                st.divider()

                # --- Articles ---
                st.subheader("🛒 Mes articles")
                try:
                    articles = json.loads(articles_json) if isinstance(articles_json, str) else articles_json
                    articles_list = articles.get("articles", [])
                except Exception:
                    articles_list = []

                if not articles_list:
                    st.write("Aucun article dans votre liste.")
                else:
                    for i, art in enumerate(articles_list):
                        cols = st.columns([3, 1, 1, 1])
                        with cols[0]:
                            st.text_input("Nom", art.get("name", ""), key=f"name_{i}", disabled=True)
                        with cols[1]:
                            st.number_input("Qté", value=float(art.get("quantite", 0)), key=f"qte_{i}", disabled=True)
                        with cols[2]:
                            st.text_input("Unité", art.get("unite", ""), key=f"unit_{i}", disabled=True)
                        with cols[3]:
                            st.button("🗑️", key=f"delete_art_{i}", disabled=True)

                st.markdown("### ➕ Ajouter un article")
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                with c1:
                    st.text_input("Nom de l'article", key="new_name", disabled=True)
                with c2:
                    st.number_input("Quantité", min_value=0.0, step=1.0, key="new_qte", disabled=True)
                with c3:
                    st.text_input("Unité", key="new_unit", disabled=True)
                with c4:
                    st.button("Ajouter", disabled=True)

                st.divider()
                st.button("🗑️ Supprimer ma liste", type="primary", disabled=True)

                cur.close()
                conn.close()

            except Exception as e:
                st.error(f"Erreur de connexion à la base de données : {e}")

        @st.dialog("🍽️ Mes recettes", width="large")
        def show_recettes():
            try:
                conn = psycopg2.connect(
                    dbname="miamigo",
                    user="postgres",
                    password="coolraoul",
                    host="postgres",
                    port="5432"
                )
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT titre_recette, source, url, ingredients
                    FROM recettes
                    WHERE user_mail = %s
                    ORDER BY titre_recette;
                    """,
                    (st.user.email,)
                )
                rows = cur.fetchall()

                if not rows:
                    st.info("Vous n'avez pas encore ajouté de recettes.")
                else:
                    for titre, source, url, ingredients_json in rows:
                        with st.expander(f"📖 {titre} ({source})", expanded=False):
                            if url:
                                st.markdown(
                                    f'<a href="{url}" target="_blank" rel="noopener noreferrer"><strong>{url}</strong></a>',
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(f"**{titre}** ({source})")

                            try:
                                if isinstance(ingredients_json, str):
                                    data = json.loads(ingredients_json)
                                elif isinstance(ingredients_json, (dict, list)):
                                    data = ingredients_json
                                else:
                                    data = {}

                                if isinstance(data, dict):
                                    ingredients = data.get("ingredients") or []
                                elif isinstance(data, list):
                                    ingredients = data
                                else:
                                    ingredients = []

                                if ingredients:
                                    st.markdown("**Ingrédients :**")
                                    for ing in ingredients:
                                        name = ing.get("name") if isinstance(ing, dict) else str(ing)
                                        quantite = ing.get("quantite") if isinstance(ing, dict) else ""
                                        unite = ing.get("unite") if isinstance(ing, dict) else ""
                                        st.write(f"- {name} {quantite} {unite}")
                                else:
                                    st.warning("Aucun ingrédient trouvé pour cette recette.")
                            except Exception as e:
                                st.error(f"Erreur lors de la lecture des ingrédients : {e}")

                            st.divider()
                            st.button(f"🗑️ Supprimer '{titre}'", key=f"delete_{titre}", type='primary', disabled=True)

                cur.close()
                conn.close()

            except Exception as e:
                st.error(f"Erreur de connexion à la base de données : {e}")

        if st.button("🧾 Ma liste de courses", use_container_width=True):
            show_liste()
        if st.button("📔 Mon livre de recettes", use_container_width=True):
            show_recettes()

        st.divider()
        st.markdown(
            """
            <div style="position: fixed; bottom: 1.5rem; left: 1.5rem; right: 1.5rem;">
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.logout()
        st.markdown("</div>", unsafe_allow_html=True)

# --- CONTENU PRINCIPAL ---
if st.user.is_logged_in:
    st.header(f"Bienvenue {st.user.name} 👋")
    st.caption("Posez vos questions à MiaMigo.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "sessionId" not in st.session_state:
        st.session_state.sessionId = str(uuid.uuid4())

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Votre message...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Attente de la réponse..."):
                try:
                    resp = requests.post(
                        "http://n8n:5678/webhook/miamigo",
                        json={
                            "message": prompt,
                            "sessionId": st.session_state.sessionId,
                            "user": st.user.email,
                        },
                        timeout=300,
                    )
                    resp.raise_for_status()
                    answer = resp.json().get("output", "")
                except Exception as e:
                    answer = f"⚠️ Erreur lors de l'appel : {e}"

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

else:
    st.warning("🔐 Connectez-vous via la barre latérale pour démarrer le chat.")
