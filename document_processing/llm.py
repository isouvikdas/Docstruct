from google import genai
import json

MAX_ATTEMPTS = 3


def get_prompt(text: str) -> str:
    return (
        "You are an AI system that extracts structured data from invoice text.\n"
        "Extract the following fields strictly in JSON format:\n"
        "invoice_number\n"
        "invoice_date\n"
        "vendor_name\n"
        "total_amount\n"
        "tax_amount\n"
        "currency\n"
        "due_date\n\n"
        "Rules:\n"
        "- Return ONLY valid JSON\n"
        "- If a field is missing, return null\n"
        "- Do not add explanations\n"
        "- Do not wrap in markdown\n"
        "- Only extract information explicitly present in the text\n\n"
        f"Invoice text:\n{text}"
    )

def get_data(text: str):
    client = genai.Client()
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=get_prompt(text),
            )

            cleaned = response.text
            data = json.loads(cleaned)

            return data

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

    return None