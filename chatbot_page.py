import streamlit as st
import random
from rag import search_food
from ai_utils import sanitize_text
from recommendation_utils import build_selected_food_context
from prompt_utils import get_chatbot_system_prompt
from prompt_utils import (
    get_chatbot_system_prompt,
    build_chatbot_prompt
)


def show_chatbot_page(client, model_name):
    data = st.session_state.last_result_context

    if not data:
        st.warning("Data rekomendasi belum tersedia. Silakan isi data terlebih dahulu.")
        if st.button("Kembali ke Menu Utama"):
            st.session_state.page = "home"
            st.rerun()
        st.stop()
        
    
    main_food_names = data.get("main_food_names", [])
    side_food_names = data.get("side_food_names", [])

    kondisi_chat = data.get("kondisi", "-")
    status_chat = data.get("status", "-")
    strategi_chat = data.get("strategi_kalori", "-")
    target_kalori_chat = data.get("target_kalori", 0)
    target_protein_chat = data.get("target_protein", 0)
    context_chat = data.get("context", {})
    df_m_chat = data.get("df_m")
    df_s_chat = data.get("df_s")
    analisis_chat = data.get("analisis_ai", "")

    selected_food_context = build_selected_food_context(df_m_chat, df_s_chat)

    st.markdown("##  NutriAI Assistant")
    st.caption(
        "Tanyakan alasan rekomendasi makanan, target kalori, protein, atau pola makan yang sesuai."
    )

    if st.button("⬅ Kembali ke Hasil Analisis", use_container_width=True):
        st.session_state.page = "result"
        st.rerun()
    

    with st.container(border=True):
        st.markdown("###  Rekomendasi Makanan")

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("####  Menu Utama")

                if main_food_names:
                    for food in main_food_names:
                        st.info(f" {food}")
                else:
                    st.caption("Belum ada menu utama.")

        with col2:
            with st.container(border=True):
                st.markdown("####  Pendamping Sehat")

                if side_food_names:
                    for food in side_food_names:
                        st.success(f" {food}")
                else:
                    st.caption("Belum ada pendamping sehat.")

        st.write("---")
        st.markdown("### Konsultasi NutriAI")

        st.caption(
            "Rekomendasi NutriAI bersifat informatif dan tidak menggantikan konsultasi tenaga kesehatan."
        )

        if not st.session_state.chatbot_messages:
            st.session_state.chatbot_messages.append({
                "role": "assistant",
                "content": (
                    f"Halo, saya NutriAI. Saya sudah membaca hasil analisis dan rekomendasi nutrisi untuk kondisi **{kondisi_chat}**.\n\n"
                    "Silakan tanyakan hal berikut:\n\n"
                    "- Alasan makanan dipilih\n"
                    "- Alternatif menu yang lebih sesuai\n"
                    "- Target kalori dan protein\n"
                    "- Pola makan harian\n"
                    "- Hidrasi, tidur, dan kebiasaan hidup"
                )
            })

        chat_area = st.container()

        with chat_area:
            for chat in st.session_state.chatbot_messages:
                if chat["role"] == "user":
                    with st.chat_message("user"):
                        st.markdown(chat["content"])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(chat["content"])

        st.markdown("#### Pertanyaan cepat")

        q1, q2, q3 = st.columns(3)

        quick_question = None

        with q1:
            if st.button("Kenapa makanan ini dipilih?", use_container_width=True):
                quick_question = "Kenapa makanan ini direkomendasikan untuk saya?"

        with q2:
            if st.button("Alternatif lebih murah", use_container_width=True):
                quick_question = "Ada alternatif makanan yang lebih murah?"

        with q3:
            if st.button("Sumber protein terbaik", use_container_width=True):
                quick_question = "Makanan mana yang paling bagus untuk memenuhi protein saya?"

        if st.button(" Bersihkan Chat", use_container_width=True):
            st.session_state.chatbot_messages = []
            st.rerun()

        typed_question = st.chat_input("Tulis pertanyaan kamu di sini...")
        user_question = quick_question if quick_question else typed_question    

        if user_question:
            st.session_state.chatbot_messages.append({
                "role": "user",
                "content": user_question
            })
            
            with chat_area:
                with st.chat_message("user"):
                    st.markdown(user_question)

                with st.chat_message("assistant"):
                    loading_box = st.empty()
                    loading_messages = [
                    "Membaca pertanyaan kamu...",
                    "Menyesuaikan dengan profil dan tujuan kesehatan...",
                    "Menyusun jawaban yang sesuai..."
                ]

                loading_box.info(
                    random.choice(loading_messages)
                )
            
            rag_results = search_food(user_question, k=3)

            rag_context = "\n\n".join(
                [doc.page_content for doc in rag_results]
            )

            chatbot_prompt = build_chatbot_prompt(
                kondisi_chat,
                status_chat,
                strategi_chat,
                target_kalori_chat,
                target_protein_chat,
                context_chat,
                analisis_chat,
                selected_food_context,
                user_question,
                rag_context
            )

            try:
                with st.spinner("NutriAI sedang menjawab..."):
                    messages = [
                        {
                            "role": "system",
                            "content": get_chatbot_system_prompt()
                        }
                    ]

                    for msg in st.session_state.chatbot_messages[-10:]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })

                    messages.append({
                        "role": "user",
                        "content": chatbot_prompt
                    })

                    chat_res = client.chat.completions.create(
                        model=model_name,
                        temperature=0.2,
                        messages=messages
                    )

                    bot_answer = sanitize_text(
                        chat_res.choices[0].message.content
                    )

                    loading_box.empty()

                    with st.chat_message("assistant"):
                        st.markdown(bot_answer)

            except Exception:
                bot_answer = (
                    "Maaf, chatbot sedang tidak stabil. "
                    "Coba tanyakan lagi dengan kalimat yang lebih singkat."
                )

            st.session_state.chatbot_messages.append({
                "role": "assistant",
                "content": bot_answer
            })

            st.rerun()