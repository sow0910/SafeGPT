import requests


DEFAULT_SYSTEM_PROMPT = (
    "[AADHAAR], [PERSON], [EMAIL], [PHONE], [PAN], etc. are anonymized placeholders created by SafeGPT. "
    "They are not actual private values. Answer the user's question normally without attempting to reveal "
    "or reconstruct the original values."
)


def ask_llm(prompt, system=DEFAULT_SYSTEM_PROMPT):
    """Send a prompt to our local Llama 3 model through Ollama."""

    payload = {
        "model": "llama3:8b",
        "prompt": prompt,
        "stream": False
    }
    if system:
        payload["system"] = system

    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload
    )

    data = response.json()

    return data["response"]


if __name__ == "__main__":

    test_prompt = "What is Artificial Intelligence?"

    answer = ask_llm(test_prompt)

    print("Llama 3 response:")
    print(answer)