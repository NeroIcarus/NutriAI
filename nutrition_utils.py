def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

def get_bmi_status(bmi):
    if bmi < 18.5:
        return "Berat Kurang"
    elif bmi < 25:
        return "Ideal"
    return "Berat Lebih"

def calculate_bmr(weight, height, age, gender):
    if gender == "Laki-laki":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    return (10 * weight) + (6.25 * height) - (5 * age) - 161

def get_activity_factor(kondisi, context):
    if isinstance(context, dict):
        text = " ".join([str(v) for v in context.values()]).lower()
    else:
        text = str(context).lower()

    if "jogging" in text or "olahraga" in text or "gym" in text or "latihan" in text:
        return 1.45

    if "kerja duduk" in text or "duduk" in text or "jarang olahraga" in text:
        return 1.2

    if kondisi == "Pemulihan":
        return 1.2

    return 1.3

def get_nutrition_strategy(bmi, kondisi, context):
    if bmi < 18.5:
        return (
            "Surplus Kalori",
            "Prioritaskan protein, karbohidrat, dan lemak sehat untuk membantu menaikkan berat badan secara bertahap."
        )

    if bmi >= 25:
        return (
            "Defisit Kalori",
            "Prioritaskan protein tinggi, serat, dan makanan dengan kalori lebih terkontrol."
        )

    if kondisi == "Harian":
        return (
            "Gizi Seimbang",
            "Prioritaskan pola makan seimbang sesuai tujuan harian seperti energi, pencernaan, tidur, atau daya tahan tubuh."
        )

    return (
        "Gizi Seimbang",
        "Prioritaskan makanan seimbang dengan protein cukup, karbohidrat sesuai kebutuhan, dan pendamping bergizi."
    )

def calculate_target_calorie(tdee, strategy):
    if strategy == "Surplus Kalori":
        return tdee + 300
    if strategy == "Defisit Kalori":
        return max(tdee - 300, 1200)
    return tdee

def get_calorie_explanation(bmr, tdee, target_kalori, strategi):
    if strategi == "Surplus Kalori":
        return (
            f"BMR kamu sekitar {bmr:.0f} kcal. Estimasi kebutuhan harian kamu sekitar {tdee:.0f} kcal. "
            f"Karena targetnya menaikkan berat badan, NutriAI menambahkan surplus sekitar 300 kcal, "
            f"jadi target harian kamu sekitar {target_kalori:.0f} kcal."
        )

    if strategi == "Defisit Kalori":
        return (
            f"BMR kamu sekitar {bmr:.0f} kcal. Estimasi kebutuhan harian kamu sekitar {tdee:.0f} kcal. "
            f"Karena targetnya menurunkan berat badan, NutriAI mengurangi sekitar 300 kcal, "
            f"jadi target harian kamu sekitar {target_kalori:.0f} kcal."
        )

    return (
        f"BMR kamu sekitar {bmr:.0f} kcal. Estimasi kebutuhan harian kamu sekitar {tdee:.0f} kcal. "
        f"Karena targetnya menjaga kondisi tubuh, target kalori harian dibuat mendekati kebutuhan harian tersebut."
    )

def calculate_target_protein(weight, strategy):
    if strategy == "Surplus Kalori":
        return weight * 1.6
    if strategy == "Defisit Kalori":
        return weight * 1.8
    return weight * 1.3

def calculate_hydration(age, gender, weight):
    if age < 18:
        factor = 0.035
    elif age >= 60:
        factor = 0.030
    else:
        factor = 0.035 if gender == "Laki-laki" else 0.031

    target_liter = weight * factor

    if target_liter < 1.5:
        target_liter = 1.5

    target_glass = round(target_liter / 0.25)
    return target_liter, target_glass

def calculate_hydration_target(berat):
    target_air = berat * 0.033
    target_gelas = round(target_air / 0.25)
    return target_air, target_gelas


def extract_hydration_glass(context):
    if isinstance(context, dict):
        return context.get("hidrasi_gelas")

    if isinstance(context, str):
        if "Hidrasi:" in context and "gelas" in context:
            try:
                hydration_text = context.split("Hidrasi:")[1].split("gelas")[0].strip()
                return int(hydration_text)
            except:
                return None

    return None

def get_hydration_status(user_glass, target_glass):
    if user_glass is None:
        return (
            "Belum diketahui",
            "Target cairan harian digunakan sebagai acuan umum. Kamu bisa menyesuaikan dengan aktivitas dan rasa haus."
        )

    if user_glass < target_glass - 1:
        kurang = target_glass - user_glass
        return (
            "Kurang",
            f"Kamu baru minum sekitar {user_glass} gelas hari ini. Tambahkan sekitar {kurang} gelas secara bertahap. Mulai dari 1 gelas setelah makan, 1 gelas saat sore, dan 1 gelas sebelum tidur."
        )

    if user_glass < target_glass:
        return (
            "Hampir cukup",
            "Asupan minum kamu hampir cukup. Tinggal tambah sekitar 1 gelas lagi untuk mendekati kebutuhan harian."
        )

    if user_glass <= target_glass + 2:
        return (
            "Cukup",
            "Asupan minum kamu sudah cukup untuk hari ini. Pertahankan pola minum yang stabil, terutama saat banyak aktivitas."
        )

    return (
        "Lebih dari target",
        "Asupan minum kamu sudah melewati kebutuhan harian. Tidak perlu dipaksa tambah banyak lagi, cukup jaga minum secara stabil sesuai rasa haus dan aktivitas."
    )