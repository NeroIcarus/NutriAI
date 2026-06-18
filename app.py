import streamlit as st
import pandas as pd
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from rag import search_food
from filter_utils import filter_by_tags
from database_utils import load_main_db, load_side_db
from chatbot_page import show_chatbot_page
from prompt_utils import (
    get_recommendation_system_prompt,
    build_recommendation_prompt
)
from nutrition_utils import (
    calculate_bmi,
    get_bmi_status,
    calculate_bmr,
    get_activity_factor,
    get_nutrition_strategy,
    calculate_target_calorie,
    get_calorie_explanation,
    calculate_target_protein,
    calculate_hydration,
    calculate_hydration_target,
    extract_hydration_glass,
    get_hydration_status
)
from health_utils import (
    get_recovery_rules,
    get_recovery_keluhan,
    get_weight_strategy,
    evaluate_weight_goal,
    get_weight_steps,
    get_weight_activity_plan
)
from recommendation_utils import (
    get_candidate_foods,
    get_rec,
    get_daily_goal,
    get_fallback_foods,
    make_safe_analysis,
    build_selected_food_context
)
from ai_utils import (
    sanitize_text,
    clean_ai_keywords
)
# =========================================================
# 1. KONFIGURASI
# =========================================================
st.set_page_config(
    page_title="NutriAI - Asisten Nutrisi",
    page_icon="N",
    layout="wide"
)

load_dotenv()

MODEL_NAME = "openrouter/free"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY belum ditemukan di file .env")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "NutriAI",
    }
)

# =========================================================
# 2. LOAD DATABASE
# =========================================================

df_main_db = load_main_db()
df_side_db = load_side_db()

# =========================================================
# 3. SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "kondisi" not in st.session_state:
    st.session_state.kondisi = None
if "berat_user" not in st.session_state:
    st.session_state.berat_user = 60
if "tinggi_user" not in st.session_state:
    st.session_state.tinggi_user = 165
if "umur_user" not in st.session_state:
    st.session_state.umur_user = 25
if "gender_user" not in st.session_state:
    st.session_state.gender_user = "Laki-laki"
if "user_context" not in st.session_state:
    st.session_state.user_context = ""
if "chatbot_messages" not in st.session_state:
    st.session_state.chatbot_messages = []
if "last_result_context" not in st.session_state:
    st.session_state.last_result_context = {}

# =========================================================
# 4. CSS
# =========================================================
st.markdown("""
<style>
div.stButton > button {
    border-radius: 50px;
}

.card-small {
    min-height: 130px;
}

.card-medium {
    min-height: 170px;
}

.card-section {
    min-height: 190px;
}

.block-container {
    padding-top: 4rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 6. TOMBOL KEMBALI
# =========================================================
if st.session_state.page != "home":
    if st.button("⬅ Kembali ke Menu Utama"):
        st.session_state.page = "home"
        st.rerun()

# =========================================================
# 7. HOME
# =========================================================
if st.session_state.page == "home":

    st.markdown("""
    <h1 style='text-align:center;'>
        <span style='color:#22C55E;'>Nutri</span>AI
    </h1>
    <p style='text-align:center; color:#94A3B8;'>
        Sistem rekomendasi nutrisi berbasis kecerdasan buatan
    </p>
    """, unsafe_allow_html=True)

    st.write("## Apa yang sedang kamu rasakan hari ini?")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader(" Sedang Tidak Fit")
            st.write("Saran makanan saat tubuh kurang fit atau pemulihan.")
            if st.button("Pilih Pemulihan", use_container_width=True):
                st.session_state.page = "input_data"
                st.session_state.kondisi = "Pemulihan"
                st.rerun()

        with st.container(border=True):
            st.subheader(" Atur Berat Badan")
            st.write("Program nutrisi untuk diet sehat atau menaikkan berat badan.")
            if st.button("Pilih Manajemen Berat", use_container_width=True):
                st.session_state.page = "input_data"
                st.session_state.kondisi = "Berat Badan"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader(" Jaga Kondisi Tubuh")
            st.write("Tips nutrisi harian agar tubuh tetap bugar.")
            if st.button("Pilih Kesehatan Harian", use_container_width=True):
                st.session_state.page = "input_data"
                st.session_state.kondisi = "Harian"
                st.rerun()
                
    st.caption(
    "NutriAI membantu memberikan rekomendasi nutrisi berdasarkan data yang diinput pengguna. "
    "Hasil tidak digunakan untuk diagnosis atau pengobatan medis."
)

# =========================================================
# 8. INPUT PAGE
# =========================================================
elif st.session_state.page == "input_data":

    c_side, c_main = st.columns([1, 2.5], gap="large")

    with c_side:
        st.markdown(f"### Detail {st.session_state.kondisi}")
        st.info("Lengkapi data agar rekomendasi makanan lebih sesuai.")

    with c_main:
        with st.form("form_input"):
            st.subheader("Profil Fisik")

            f_col1, f_col2, f_col3, f_col4 = st.columns(4)

            umur = f_col1.number_input("Umur", min_value=1, max_value=120, value=25)
            gender = f_col2.selectbox("Gender", ["Laki-laki", "Perempuan"])
            tinggi = f_col3.number_input("Tinggi (cm)", min_value=50, max_value=250, value=165)
            berat = f_col4.number_input("Berat (kg)", min_value=10, max_value=300, value=60)

            st.write("---")

            extra_context = {}

            if st.session_state.kondisi == "Harian":
                st.subheader("Analisis Gaya Hidup")

                col_h1, col_h2 = st.columns(2)

                tidur_range = col_h1.selectbox(
                    "Durasi tidur",
                    ["kurang dari 5 jam", "5-6 jam", "6-8 jam", "lebih dari 8 jam"]
                )

                jam_mulai_tidur = col_h2.time_input("Jam mulai tidur")

                hidrasi_gelas = st.number_input(
                    "Minum air hari ini (gelas)",
                    min_value=0,
                    max_value=20,
                    value=8
                )

                aktivitas_desc = st.text_area(
                    "Deskripsikan rutinitas",
                    placeholder="Contoh: kerja duduk 8 jam, jogging 20 menit"
                )

                target_sehat = st.multiselect(
                    "Pilih tujuan kesehatan harian kamu",
                    [
                        "Meningkatkan daya tahan tubuh",
                        "Menambah energi untuk aktivitas harian",
                        "Membantu pencernaan lebih nyaman",
                        "Membantu tubuh terasa lebih segar",
                        "Mendukung kualitas tidur",
                        "Menjaga pola makan seimbang",
                        "Mengurangi rasa lemas",
                        "Menjaga berat badan tetap stabil"
                    ]
                )

                keluhan_kecil = st.text_input("Keluhan ringan")

                extra_context = {
                    "tidur": tidur_range,
                    "jam_tidur": str(jam_mulai_tidur),
                    "hidrasi_gelas": hidrasi_gelas,
                    "aktivitas": aktivitas_desc,
                    "tujuan": target_sehat,
                    "keluhan": keluhan_kecil
                }

            elif st.session_state.kondisi == "Pemulihan":
                st.subheader("Detail Pemulihan")

                keluhan = st.selectbox(
                    "Apa yang sedang kamu rasakan?",
                    [
                        "Maag / Asam lambung",
                        "Diare",
                        "Demam / Flu",
                        "Lemas / Tidak enak badan"
                    ]
                )

                col_p1, col_p2 = st.columns(2)

                durasi = col_p1.selectbox(
                    "Sudah berapa lama terasa?",
                    [
                        "Hari ini",
                        "1-2 hari",
                        "3-5 hari",
                        "Lebih dari 5 hari"
                    ]
                )

                nafsu_makan = col_p2.selectbox(
                    "Nafsu makan kamu sekarang",
                    [
                        "Normal",
                        "Berkurang",
                        "Sangat berkurang"
                    ]
                )

                gejala_tambahan = st.multiselect(
                    "Keluhan tambahan yang kamu rasakan",
                    [
                        "Mual",
                        "Muntah",
                        "Pusing",
                        "Lemas",
                        "Kembung",
                        "Tenggorokan tidak nyaman",
                        "Sering buang air besar",
                        "Tidak ada"
                    ]
                )

                makanan_terakhir = st.selectbox(
                    "Makanan terakhir yang masih nyaman dimakan",
                    [
                        "Belum makan",
                        "Bubur",
                        "Roti",
                        "Nasi",
                        "Buah",
                        "Makanan berkuah",
                        "Makanan biasa"
                    ]
                )

                pantangan = st.text_area(
                    "Alergi atau makanan yang ingin dihindari",
                    placeholder="Contoh: alergi seafood, tidak bisa susu, tidak suka pedas"
                )

                extra_context = {
                    "keluhan": keluhan,
                    "durasi": durasi,
                    "nafsu_makan": nafsu_makan,
                    "gejala_tambahan": gejala_tambahan,
                    "makanan_terakhir": makanan_terakhir,
                    "pantangan": pantangan
                }

            elif st.session_state.kondisi == "Berat Badan":
                st.subheader("Target Manajemen Berat Badan")

                col_b1, col_b2 = st.columns(2)

                tujuan_berat = col_b1.selectbox(
                    "Tujuan berat badan",
                    [
                        "Menurunkan berat badan",
                        "Menaikkan berat badan",
                        "Menjaga berat badan"
                    ]
                )

                target_berat = col_b2.number_input(
                    "Target berat (kg)",
                    min_value=20,
                    value=55
                )

                target_bulan = st.number_input(
                    "Target waktu (bulan)",
                    min_value=1,
                    max_value=60,
                    value=6
                )

                extra_context = {
                    "tujuan_berat": tujuan_berat,
                    "target_berat": target_berat,
                    "target_bulan": target_bulan
                }

            submit = st.form_submit_button(
                "Dapatkan Analisis NutriAI",
                use_container_width=True
            )

            if submit:
                    st.session_state.umur_user = umur
                    st.session_state.gender_user = gender
                    st.session_state.berat_user = berat
                    st.session_state.tinggi_user = tinggi
                    st.session_state.user_context = extra_context
                    st.session_state.last_result_context = {}
                    st.session_state.page = "result"
                    st.rerun()

# =========================================================
# 9. RESULT PAGE
# =========================================================
elif st.session_state.page == "result":

    b_val = st.session_state.berat_user
    t_val = st.session_state.tinggi_user
    umur_user = st.session_state.umur_user
    gender_user = st.session_state.gender_user
    context = st.session_state.user_context
    kondisi = st.session_state.kondisi

    bmi = calculate_bmi(b_val, t_val)
    status = get_bmi_status(bmi)

    bmr = calculate_bmr(b_val, t_val, umur_user, gender_user)
    activity_factor = get_activity_factor(kondisi, context)
    tdee = bmr * activity_factor

    strategi_kalori, strategi_penjelasan = get_nutrition_strategy(bmi, kondisi, context)
    target_kalori = calculate_target_calorie(tdee, strategi_kalori)
    target_protein = calculate_target_protein(b_val, strategi_kalori)

    if kondisi == "Berat Badan":
        strategi_kalori = get_weight_strategy(context)
        target_kalori = calculate_target_calorie(tdee, strategi_kalori)
        target_protein = calculate_target_protein(b_val, strategi_kalori)

    target_air, target_gelas = calculate_hydration(umur_user, gender_user, b_val)
    hidrasi_gelas_user = extract_hydration_glass(context)
    hidrasi_status, hidrasi_saran = get_hydration_status(hidrasi_gelas_user, target_gelas)

    fallback_main, fallback_side = get_fallback_foods(kondisi, context, strategi_kalori)

    main_context = get_candidate_foods(df_main_db, 70)
    side_context = get_candidate_foods(df_side_db, 70)
# =====================================================
# KHUSUS SEDANG TIDAK FIT
# =====================================================

    avoid_foods = []

    if kondisi == "Pemulihan":

        keluhan = get_recovery_keluhan(context)

        rules = get_recovery_rules(keluhan)

        fallback_main = rules["main"]
        fallback_side = rules["side"]
        avoid_foods = rules["avoid"]
        priority_recovery = rules["priority"]
        hydration_recovery = rules["hydration"]
        warning_recovery = rules["warning"]


    prompt = build_recommendation_prompt(
        umur_user,
        gender_user,
        t_val,
        b_val,
        bmi,
        status,
        bmr,
        tdee,
        target_kalori,
        target_protein,
        strategi_kalori,
        strategi_penjelasan,
        kondisi,
        context,
        hidrasi_status,
        target_gelas,
        target_air,
        main_context,
        side_context
    )

    analisis_ai = make_safe_analysis(
        kondisi,
        status,
        strategi_kalori,
        target_kalori,
        target_protein,
        context
    )
    main_k = ", ".join(fallback_main)
    side_k = ", ".join(fallback_side)

    try:
        with st.spinner("NutriAI sedang merancang menu..."):
            res = client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0.1,
                messages=[
                    {
                        "role": "system",
                        "content": get_recommendation_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            ai_raw = sanitize_text(res.choices[0].message.content)

            if "ANALISIS:" in ai_raw and "MAIN_COURSE:" in ai_raw and "SIDE_DISH:" in ai_raw:
                ai_analysis_candidate = (
                    ai_raw
                    .split("MAIN_COURSE:")[0]
                    .replace("ANALISIS:", "")
                    .strip()
                )

                ai_main_candidate = (
                    ai_raw
                    .split("MAIN_COURSE:")[1]
                    .split("SIDE_DISH:")[0]
                    .replace("[", "")
                    .replace("]", "")
                    .strip()
                )

                ai_side_candidate = (
                    ai_raw
                    .split("SIDE_DISH:")[1]
                    .replace("[", "")
                    .replace("]", "")
                    .strip()
                )

                ai_main_candidate = clean_ai_keywords(ai_main_candidate)
                ai_side_candidate = clean_ai_keywords(ai_side_candidate)

                if len(ai_analysis_candidate.split()) >= 10:
                    analisis_ai = ai_analysis_candidate

                if kondisi != "Harian":
                    main_k = ai_main_candidate if ai_main_candidate else main_k
                    side_k = ai_side_candidate if ai_side_candidate else side_k

    except Exception as e:
        st.warning("AI sedang tidak stabil. Sistem memakai rekomendasi dari logic NutriAI.")

    filtered_main_db = filter_by_tags(
            df_main_db,
            kondisi,
            strategi_kalori
    )

    filtered_side_db = filter_by_tags(
            df_side_db,
            kondisi,
            strategi_kalori
    )

    df_m = get_rec(
            filtered_main_db,
            main_k,
            fallback_main
    )

    df_s = get_rec(
            filtered_side_db,
            side_k,
            fallback_side
    )
    
    if not st.session_state.last_result_context:
        st.session_state.last_result_context = {
            "kondisi": kondisi,
            "status": status,
            "strategi_kalori": strategi_kalori,
            "target_kalori": target_kalori,
            "target_protein": target_protein,
            "context": context,
            "df_m": df_m.copy(),
            "df_s": df_s.copy(),
            "analisis_ai": analisis_ai,
            "main_food_names": df_m["nama_asli"].tolist() if not df_m.empty else [],
            "side_food_names": df_s["nama_asli"].tolist() if not df_s.empty else []
        }
        
    else:
        saved = st.session_state.last_result_context
        df_m = saved["df_m"]
        df_s = saved["df_s"]
        analisis_ai = saved["analisis_ai"]

    # =====================================================
    # UI HASIL
    # =====================================================
    st.markdown("## Laporan Nutrisi Personal")

    with st.container(border=True):
        st.info(f"**Analisis NutriAI:** {analisis_ai}")

    c1, c2, c3 = st.columns(3)

    if kondisi == "Harian":

        with c1:
            with st.container(border=True):
                st.caption("Tujuan")
                tujuan = context.get("tujuan", [])

                if isinstance(tujuan, list):
                    if tujuan:
                        for item in tujuan:
                            st.write(f"• {item}")
                    else:
                        st.write("Menjaga kondisi tubuh harian")
                else:
                    st.write(tujuan)

        with c2:
            with st.container(border=True):
                st.metric("Target Cairan", f"{target_air:.1f} Liter")

                if hidrasi_gelas_user is not None:
                    st.caption(
                        f"Minum hari ini: {hidrasi_gelas_user} gelas "
                        f"(target sekitar {target_gelas} gelas)"
                    )

                st.caption(f"Status: {hidrasi_status}")
                st.caption(hidrasi_saran)

        with c3:
            with st.container(border=True):
                st.metric("Status Tubuh", status)
                st.caption(f"BMI: {bmi:.1f}")

    elif kondisi == "Pemulihan":

        keluhan_user = context.get("keluhan", "Sedang Tidak Fit")
        durasi_user = context.get("durasi", "-")
        nafsu_user = context.get("nafsu_makan", "-")

        with c1:
            with st.container(border=True):
                st.metric("Kondisi", keluhan_user)

        with c2:
            with st.container(border=True):
                st.metric("Durasi", durasi_user)

        with c3:
            with st.container(border=True):
                st.metric("Nafsu Makan", nafsu_user)

        with st.container(border=True):
            st.markdown("###  Prioritas Pemulihan")
            for item in priority_recovery:
                st.write(f"• {item}")

        with st.container(border=True):
            st.markdown("###  Hidrasi Saat Pemulihan")
            st.info(hydration_recovery)

        with st.container(border=True):
            st.markdown("###  Makanan yang Sebaiknya Dihindari")
            for item in avoid_foods:
                st.write(f"• {item}")

        with st.container(border=True):
            st.markdown("###  Kapan Harus Waspada")
            for item in warning_recovery:
                st.write(f"• {item}")

    elif kondisi == "Berat Badan":

        tujuan_berat = context.get("tujuan_berat", "-")
        target_berat = context.get("target_berat", b_val)
        target_bulan = context.get("target_bulan", 6)

        selisih_berat = target_berat - b_val

        evaluasi = evaluate_weight_goal(
            b_val,
            target_berat,
            target_bulan
        )

        langkah_makan = get_weight_steps(strategi_kalori)
        aktivitas_plan = get_weight_activity_plan(strategi_kalori)

        with c1:
            with st.container(border=True):
                st.metric("Status Tubuh", status)
                st.caption(f"BMI: {bmi:.1f}")

        with c2:
            with st.container(border=True):
                st.metric("Evaluasi Target", evaluasi["status"])
                st.caption(evaluasi["message"])

        with c3:
            with st.container(border=True):
                st.metric("Strategi", strategi_kalori)
                st.caption(f"Target waktu: {target_bulan} bulan")

        with st.container(border=True):
            st.markdown("###  Ringkasan Target")

            r1, r2, r3, r4 = st.columns(4)

            r1.metric("Berat Saat Ini", f"{b_val:.1f} kg")
            r2.metric("Target Berat", f"{target_berat:.1f} kg")
            r3.metric("Perubahan", f"{abs(selisih_berat):.1f} kg")
            r4.metric("Waktu", f"{target_bulan} bulan")

        with st.container(border=True):
            st.markdown("###  Kebutuhan Kalori")

            k1, k2, k3, k4 = st.columns(4)

            k1.metric("BMR", f"{bmr:.0f} kcal")
            k2.metric("TDEE", f"{tdee:.0f} kcal")
            k3.metric("Target Kalori", f"{target_kalori:.0f} kcal")
            k4.metric("Target Protein", f"{target_protein:.0f} g")

            st.info(
                f"""
                BMR adalah kebutuhan kalori dasar tubuh saat tubuh beristirahat.

                TDEE adalah estimasi total kebutuhan kalori harian berdasarkan aktivitas.

                Target kalori disesuaikan dengan strategi {strategi_kalori.lower()}.
                """
            )

        kg_per_bulan = abs(selisih_berat) / target_bulan
        kg_per_minggu = kg_per_bulan / 4

        with st.container(border=True):
            st.markdown("###  Saran Target")

            st.info(
                f"Untuk mencapai target ini, perubahan rata-rata yang dibutuhkan sekitar "
                f"{kg_per_bulan:.1f} kg per bulan atau {kg_per_minggu:.1f} kg per minggu."
            )

            for item in evaluasi["suggestion"]:
                st.write(f"• {item}")

        with st.container(border=True):
            st.markdown("###  Langkah Pola Makan")
            for item in langkah_makan:
                st.write(f"• {item}")

        with st.container(border=True):
            st.markdown("###  Aktivitas Pendukung")
            for item in aktivitas_plan:
                st.write(f"• {item}")

    st.write("---")
    main_focus_display = ", ".join(df_m["nama_asli"].tolist()) if not df_m.empty else main_k
    st.markdown(f"###  Menu Utama (Fokus: {main_focus_display})")

    if df_m.empty:
        st.warning("Menu utama belum ditemukan di database.")
    else:
        cols_m = st.columns(3)

        for i, (_, row) in enumerate(df_m.iterrows()):
            with cols_m[i]:
                with st.container(border=True):
                    st.write(f"#### {row['nama_asli']}")

                    if "kategori_asal" in row:
                        st.caption(f"Kategori: {row['kategori_asal']}")

                    if "kalori" in row and "protein" in row:
                        st.caption(
                            f"**Kandungan Gizi:** {row['kalori']} kcal | Protein: {row['protein']}g"
                        )

                    if "saran_ai" in row:
                        st.info(f"**Manfaat Gizi:** {row['saran_ai']}")

    side_focus_display = ", ".join(df_s["nama_asli"].tolist()) if not df_s.empty else side_k
    st.markdown(f"###  Pendamping Sehat (Fokus: {side_focus_display})")

    if df_s.empty:
        st.warning("Pendamping sehat belum ditemukan di database.")
    else:
        cols_s = st.columns(3)

        for i, (_, row) in enumerate(df_s.iterrows()):
            with cols_s[i]:
                with st.container(border=True):
                    st.write(f"#### {row['nama_asli']}")

                    if "kategori_asal" in row:
                        st.caption(f"Kategori: {row['kategori_asal']}")

                    if "kalori" in row and "protein" in row:
                        st.caption(
                            f"**Kandungan Gizi:** {row['kalori']} kcal | Protein: {row['protein']}g"
                        )

                    if "saran_ai" in row:
                        st.success(f"**Manfaat Gizi:** {row['saran_ai']}")
                
    st.write("---")
    with st.container(border=True):
        st.markdown("###  Masih ingin bertanya?")
        st.caption("Lanjutkan ke halaman chat untuk bertanya lebih detail tentang rekomendasi makanan kamu.")
        
        st.divider()

        st.info(
            "Informasi dan rekomendasi NutriAI bersifat edukatif. "
            "Jika keluhan tidak membaik, memburuk, atau mengganggu aktivitas sehari-hari, "
            "sebaiknya konsultasikan dengan tenaga kesehatan."
        )

        if st.button("Konsultasi dengan NutriAI", use_container_width=True):
            st.session_state.page = "chatbot"
            st.session_state.chatbot_messages = []
            st.rerun()
    
elif st.session_state.page == "chatbot":
    show_chatbot_page(client, MODEL_NAME)
            
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#94a3b8; font-size:0.8rem;'>© 2026 NutriAI Project.</p>",
        unsafe_allow_html=True
    )