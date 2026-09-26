from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

system_prompt = """
You are a friendly AI assistant.
Answer clearly and simply.
"""

generation_config = {
    "response_mime_type": "application/json"
}

last_interaction_id = None

while True:
    user_input = input("YOU: ").strip()

    if user_input.lower() == "exit":
        print("AI : Goodbye!")
        break

    if last_interaction_id is None:
        response = client.interactions.create(
            model="gemini-3.6-flash",
            system_instruction=system_prompt,
            input=user_input,
            response_format=generation_config,
        )
    else:
        response = client.interactions.create(
            model="gemini-3.6-flash",
            system_instruction=system_prompt,
            input=user_input,
            previous_interaction_id=last_interaction_id,
            response_format=generation_config,
        )

    print("AI:", response.output_text)

    last_interaction_id = response.id