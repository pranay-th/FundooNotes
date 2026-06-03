from openrouter import OpenRouter
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "fundoonotes", ".env"))

# Conversation history — persists for the entire session
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Remember the full conversation and answer follow-up questions accordingly."
    }
]

with OpenRouter(
    api_key=os.getenv("OPENROUTER_API_KEY", ""),
) as llm:
    print("Chatbot ready. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("Bye!")
            break
        if not question:
            continue

        # Append user message to history
        messages.append({"role": "user", "content": question})

        response = llm.chat.send(
            model="openai/gpt-3.5-turbo",
            messages=messages
        )

        answer = response.choices[0].message.content

        # Append assistant reply to history so it remembers it
        messages.append({"role": "assistant", "content": answer})

        print(f"\nBot: {answer}\n")
