import streamlit as st
from health_utils import get_recovery_keluhan, get_recovery_rules

def filter_by_tags(df, kondisi, strategi):
    if df is None or df.empty:
        return df

    result = df.copy()
    
    pantangan_text = str(
        st.session_state.user_context.get("pantangan", "")
    ).lower()

    if pantangan_text and "nama_asli" in result.columns:
        stopwords = [
            "gak", "ga", "nggak", "tidak", "bisa", "makan",
            "suka", "alergi", "saya", "aku", "gw", "gue",
            "ingin", "hindari", "menghindari", "tanpa",
            "jangan", "pakai", "pake", "boleh"
        ]

        pantangan_words = [
            word.strip()
            for word in pantangan_text.replace(",", " ").split()
            if len(word.strip()) > 2 and word.strip() not in stopwords
        ]

        if pantangan_words:
            result = result[
                ~result["nama_asli"]
                .astype(str)
                .str.lower()
                .apply(lambda food_name: any(word in food_name for word in pantangan_words))
            ]

    for col in ["mudah_dicerna", "tinggi_protein", "tinggi_kalori", "tinggi_serat", "rendah_lemak", "tinggi_air", "laktosa", "asam", "pedas", "berminyak", "kafein"]:
        if col in result.columns:
            result[col] = result[col].astype(str).str.lower()

    if kondisi == "Pemulihan":
        keluhan = get_recovery_keluhan(st.session_state.user_context)
        
        rules = get_recovery_rules(keluhan)
        avoid_foods = rules.get("avoid", [])

        if avoid_foods and "nama_asli" in result.columns:
            result = result[
                ~result["nama_asli"].astype(str).str.lower().isin(
                    [food.lower() for food in avoid_foods]
                )
            ]

        if keluhan == "Maag / Asam lambung":
            if "asam" in result.columns:
                result = result[result["asam"] != "ya"]
            if "pedas" in result.columns:
                result = result[result["pedas"] != "ya"]
            if "berminyak" in result.columns:
                result = result[result["berminyak"] != "ya"]
            if "kafein" in result.columns:
                result = result[result["kafein"] != "ya"]
            if "tinggi_serat" in result.columns:
                result = result[result["tinggi_serat"] != "ya"]

        elif keluhan == "Diare":
            if "kategori_asal" in result.columns:
                has_fruit = result["kategori_asal"].astype(str).str.lower().eq("fruit").any()

                if has_fruit:
                    result = result[
                        result["kategori_asal"].astype(str).str.lower() == "fruit"
                    ]

            if "laktosa" in result.columns:
                result = result[result["laktosa"] != "ya"]

            if "pedas" in result.columns:
                result = result[result["pedas"] != "ya"]

            if "berminyak" in result.columns:
                result = result[result["berminyak"] != "ya"]

            if "asam" in result.columns:
                result = result[result["asam"] != "ya"]

    if strategi == "Defisit Kalori":
        if "tinggi_kalori" in result.columns:
            result = result[result["tinggi_kalori"] != "ya"]

    return result