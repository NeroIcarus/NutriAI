import pandas as pd

def get_candidate_foods(df, limit=70):
    if df is None or df.empty:
        return "Database kosong."

    cols = ["nama_asli", "kalori", "protein", "kategori_asal", "saran_ai"]
    available_cols = [col for col in cols if col in df.columns]

    return df[available_cols].head(limit).to_string(index=False)

def get_rec(df, keywords, fallback_names=None):
    if df is None or df.empty:
        return pd.DataFrame()

    if "nama_asli" not in df.columns:
        return pd.DataFrame()

    words = [
        word.strip().replace(".", "")
        for word in keywords.replace("[", "").replace("]", "").replace("*", "").split(",")
        if word.strip()
    ]

    matched_rows = []

    for word in words:
        exact_match = df[df["nama_asli"].str.lower() == word.lower()]
        if not exact_match.empty:
            matched_rows.append(exact_match)

    if matched_rows:
        result = pd.concat(matched_rows).drop_duplicates()

        if len(result) < 3 and fallback_names:
            fallback_df = df[df["nama_asli"].isin(fallback_names)]
            result = pd.concat([result, fallback_df]).drop_duplicates()

        return result.head(3)

    if fallback_names:
        fallback_df = df[df["nama_asli"].isin(fallback_names)]
        if not fallback_df.empty:
            return fallback_df.head(3)

    return df.sample(min(3, len(df)))

def get_daily_goal(context):
    tujuan = context.get("tujuan", [])

    if not tujuan:
        return "Kesehatan Harian"

    if isinstance(tujuan, list):
        return ", ".join(tujuan)

    return str(tujuan)

def get_fallback_foods(kondisi, context, strategy):
    fallback_main = ["Dada Ayam Fillet", "Nasi Putih", "Tahu Putih"]
    fallback_side = ["Pisang", "Semangka", "Bayam Hijau"]

    if strategy == "Surplus Kalori":
        fallback_main = ["Paha Ayam", "Nasi Putih", "Telur Ayam Negeri"]
        fallback_side = ["Pisang", "Buah Alpukat", "Susu Sapi Murni"]

    elif strategy == "Defisit Kalori":
        fallback_main = ["Dada Ayam Fillet", "Ikan Nila", "Tahu Putih"]
        fallback_side = ["Bayam Hijau", "Labu Siam", "Pepaya"]

    elif strategy == "Gizi Seimbang":
        fallback_main = ["Dada Ayam Fillet", "Nasi Putih", "Ikan Kembung"]
        fallback_side = ["Bayam Hijau", "Pisang", "Semangka"]

    if kondisi == "Harian":
        tujuan = context.get("tujuan", [])

        if "Meningkatkan daya tahan tubuh" in tujuan:
            fallback_main = ["Dada Ayam Fillet", "Ikan Kembung", "Telur Ayam Negeri"]
            fallback_side = ["Jambu Biji Merah", "Jeruk Pontianak", "Bayam Hijau"]

        elif "Mendukung kualitas tidur" in tujuan:
            fallback_main = ["Tahu Putih", "Ikan Dori", "Kentang"]
            fallback_side = ["Pisang", "Susu Kedelai", "Almond"]

        elif "Membantu pencernaan lebih nyaman" in tujuan:
            fallback_main = ["Nasi Putih", "Kentang", "Tahu Putih"]
            fallback_side = ["Pepaya", "Pisang", "Labu Siam"]

        elif "Menambah energi untuk aktivitas harian" in tujuan:
            fallback_main = ["Nasi Putih", "Ubi Jalar", "Dada Ayam Fillet"]
            fallback_side = ["Pisang", "Buah Alpukat", "Kacang Hijau"]
    return fallback_main, fallback_side

def make_safe_analysis(kondisi, status, strategi, target_kalori, target_protein, context):
    tujuan = get_daily_goal(context)

    if kondisi == "Harian":
        return (
            f"Fokus kamu adalah {tujuan.lower()}. Dengan status tubuh {status}, "
            f"target harian sekitar {target_kalori:.0f} kcal dan protein sekitar {target_protein:.0f} gram. "
            f"Rekomendasi dipilih untuk mendukung kebutuhan energi, protein, dan nutrisi harian secara seimbang."
        )

    if kondisi == "Pemulihan":
        return (
            f"Kondisi tubuh sedang kurang fit, jadi makanan sebaiknya mudah dicerna, tidak terlalu berminyak, "
            f"dan tetap mengandung protein. Dengan status {status}, rekomendasi diarahkan untuk mendukung energi dan pemulihan harian."
        )

    return (
        f"Strategi nutrisi kamu adalah {strategi}. Target harian sekitar {target_kalori:.0f} kcal "
        f"dengan protein sekitar {target_protein:.0f} gram. Rekomendasi dipilih agar asupan lebih sesuai dengan tujuan berat badan."
    )
    
def build_selected_food_context(df_m, df_s):
    food_text = ""

    if df_m is not None and not df_m.empty:
        food_text += "MENU UTAMA:\n"
        for _, row in df_m.iterrows():
            food_text += (
                f"- {row['nama_asli']} | "
                f"Kalori: {row['kalori']} kcal | "
                f"Protein: {row['protein']} g | "
                f"Manfaat: {row.get('saran_ai', '-')}\n"
            )

    if df_s is not None and not df_s.empty:
        food_text += "\nPENDAMPING SEHAT:\n"
        for _, row in df_s.iterrows():
            food_text += (
                f"- {row['nama_asli']} | "
                f"Kalori: {row['kalori']} kcal | "
                f"Protein: {row['protein']} g | "
                f"Manfaat: {row.get('saran_ai', '-')}\n"
            )

    return food_text