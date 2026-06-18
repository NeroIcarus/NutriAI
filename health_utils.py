def get_recovery_rules(keluhan):

    if keluhan == "Maag / Asam lambung":
        return {
            "main": [
                "Nasi Putih",
                "Kentang",
                "Tahu Putih",
                "Ikan Dori",
                "Ikan Nila"
            ],
            "side": [
                "Pisang",
                "Pepaya",
                "Labu Siam"
            ],
            "avoid": [
                "Jeruk",
                "Tomat",
                "Mangga",
                "Sirsak"
            ],

            "priority": [
                "Menenangkan lambung",
                "Mengurangi iritasi lambung",
                "Menjaga jadwal makan teratur"
            ],

            "hydration": "Minum air putih cukup. Hindari kopi, soda, dan minuman terlalu asam.",

            "warning": [
                "Nyeri semakin berat",
                "Muntah terus menerus",
                "Sulit menelan",
                "Keluhan tidak membaik"
            ]
        }

    elif keluhan == "Diare":
        return {
            "main": [
                "Nasi Putih",
                "Kentang",
                "Tahu Putih",
                "Telur Ayam Negeri"
            ],
            "side": [
                "Pisang",
                "Apel Merah"
            ],
            "avoid": [
                "Susu Sapi Murni",
                "Yogurt Plain",
                "Kacang Merah",
                "Brokoli",
                "Kol Putih",
                "pepaya"
            ],

            "priority": [
                "Mengganti cairan yang hilang",
                "Menjaga energi tubuh",
                "Mengurangi iritasi saluran cerna"
            ],

            "hydration": "Perbanyak air putih dan pertimbangkan oralit karena tubuh kehilangan banyak cairan melalui BAB cair.",

            "warning": [
                "BAB berdarah",
                "Diare lebih dari 3 hari",
                "Tidak bisa makan atau minum",
                "Tanda dehidrasi berat"
            ]
        }

    elif keluhan == "Demam / Flu":
        return {
            "main": [
                "Dada Ayam Fillet",
                "Telur Ayam Negeri",
                "Ikan Kembung"
            ],
            "side": [
                "Jambu Biji Merah",
                "Jeruk",
                "Semangka"
            ],
            "avoid": [
                "Makanan terlalu berminyak"
            ],

            "priority": [
                "Mendukung daya tahan tubuh",
                "Menjaga hidrasi",
                "Memenuhi kebutuhan energi"
            ],

            "hydration": "Minum lebih sering walaupun tidak merasa haus karena demam meningkatkan kebutuhan cairan tubuh.",

            "warning": [
                "Demam lebih dari 3 hari",
                "Sesak napas",
                "Sulit makan atau minum",
                "Kondisi semakin memburuk"
            ]
        }

    else:
        return {
            "main": [
                "Nasi Putih",
                "Ubi Jalar",
                "Paha Ayam"
            ],
            "side": [
                "Pisang",
                "Buah Alpukat",
                "Semangka"
            ],
            "avoid": [
                "Makanan terlalu berminyak"
            ],

            "priority": [
                "Mengembalikan energi",
                "Menjaga hidrasi",
                "Memenuhi kebutuhan nutrisi"
            ],

            "hydration": "Pastikan asupan cairan tetap cukup sepanjang hari agar tubuh tidak semakin lemas.",

            "warning": [
                "Lemas lebih dari 1 minggu",
                "Pusing berat",
                "Penurunan berat badan drastis",
                "Sulit beraktivitas normal"
            ]
        }
    
def get_recovery_keluhan(context):

    if isinstance(context, dict):
        return context.get("keluhan", "")

    text = str(context).lower()

    if "maag" in text or "asam lambung" in text:
        return "Maag / Asam lambung"

    if "diare" in text:
        return "Diare"

    if "demam" in text or "flu" in text:
        return "Demam / Flu"

    if "lemas" in text or "tidak enak badan" in text:
        return "Lemas / Tidak enak badan"

    return "Lemas / Tidak enak badan"

def get_weight_strategy(context):
    tujuan = context.get("tujuan_berat", "")

    if tujuan == "Menurunkan berat badan":
        return "Defisit Kalori"

    if tujuan == "Menaikkan berat badan":
        return "Surplus Kalori"

    return "Gizi Seimbang"


def evaluate_weight_goal(current_weight, target_weight, target_bulan):
    selisih = target_weight - current_weight
    perubahan = abs(selisih)
    perubahan_per_bulan = perubahan / target_bulan

    if perubahan == 0:
        return {
            "status": "Stabil",
            "message": "Target kamu sama dengan berat saat ini.",
            "suggestion": [
                "Pertahankan pola makan seimbang.",
                "Pantau berat badan setiap minggu.",
                "Jaga aktivitas fisik rutin."
            ]
        }

    if perubahan_per_bulan <= 2:
        status = "Realistis"
        message = (
            f"Target perubahan {perubahan:.1f} kg dalam {target_bulan} bulan "
            f"setara sekitar {perubahan_per_bulan:.1f} kg per bulan. "
            "Target ini masih realistis."
        )

    elif perubahan_per_bulan <= 4:
        status = "Menantang"
        message = (
            f"Target perubahan {perubahan:.1f} kg dalam {target_bulan} bulan "
            f"setara sekitar {perubahan_per_bulan:.1f} kg per bulan. "
            "Target ini cukup menantang dan butuh konsistensi tinggi."
        )

    else:
        status = "Terlalu agresif"
        message = (
            f"Target perubahan {perubahan:.1f} kg dalam {target_bulan} bulan "
            f"setara sekitar {perubahan_per_bulan:.1f} kg per bulan. "
            "Target ini terlalu agresif jika dilakukan secara sehat."
        )

    if selisih > 0:
        suggestion = [
            "Naikkan kalori secara bertahap.",
            "Fokus pada protein, karbohidrat, dan lemak sehat.",
            "Latihan beban lebih disarankan daripada hanya menambah porsi makan."
        ]
    else:
        suggestion = [
            "Turunkan kalori secara bertahap.",
            "Fokus pada protein dan serat agar lebih kenyang.",
            "Gabungkan pola makan terkontrol dengan aktivitas fisik rutin."
        ]

    return {
        "status": status,
        "message": message,
        "suggestion": suggestion
    }


def get_weight_steps(strategi):
    if strategi == "Defisit Kalori":
        return [
            "Kurangi kalori secara bertahap, jangan ekstrem.",
            "Prioritaskan protein agar massa otot tetap terjaga.",
            "Batasi minuman manis dan makanan tinggi minyak.",
            "Perbanyak sayur dan makanan tinggi serat."
        ]

    if strategi == "Surplus Kalori":
        return [
            "Tambah porsi makan secara bertahap.",
            "Prioritaskan protein, karbohidrat, dan lemak sehat.",
            "Tambah camilan bergizi di antara jam makan.",
            "Jangan hanya menaikkan kalori dari makanan manis."
        ]

    return [
        "Jaga porsi makan tetap stabil.",
        "Penuhi protein harian.",
        "Pertahankan pola makan seimbang.",
        "Pantau berat badan secara berkala."
    ]


def get_weight_activity_plan(strategi):
    if strategi == "Defisit Kalori":
        return [
            "Jalan cepat 30-45 menit, 3-5 kali per minggu.",
            "Latihan beban 2-3 kali per minggu.",
            "Jogging ringan atau bersepeda jika tubuh sudah terbiasa."
        ]

    if strategi == "Surplus Kalori":
        return [
            "Latihan beban 3-4 kali per minggu.",
            "Fokus progressive overload secara bertahap.",
            "Batasi kardio berlebihan agar surplus kalori tidak terlalu banyak terpakai."
        ]

    return [
        "Jalan kaki rutin setiap hari.",
        "Latihan beban ringan 2-3 kali per minggu.",
        "Lakukan peregangan atau aktivitas ringan agar tubuh tetap aktif."
    ]
