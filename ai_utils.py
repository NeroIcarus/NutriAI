import re

def sanitize_text(text):
    if not text:
        return ""

    text = re.sub(r"<\/?assistant>", "", text)
    text = re.sub(r"<\/?user>", "", text)
    text = re.sub(r"<\/?system>", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = text.replace("```", "")
    text = text.replace("*", "")
    text = text.strip()

    return text


def clean_ai_keywords(text):
    text = sanitize_text(text)

    banned_words = [
        "bakar", "goreng", "rebus", "kukus", "panggang",
        "sup", "sop", "fillet", "segar", "matang"
    ]

    cleaned_items = []

    for item in text.split(","):
        food = item.strip().replace(".", "")

        for word in banned_words:
            food = food.replace(word.title(), "")
            food = food.replace(word.lower(), "")

        food = " ".join(food.split())

        if food:
            cleaned_items.append(food)

    return ", ".join(cleaned_items)