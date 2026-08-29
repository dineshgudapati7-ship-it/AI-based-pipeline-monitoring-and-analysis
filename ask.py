"""
ask.py
The actual "RAG" step:
1. Take a natural-language question
2. Search Chroma for the most relevant log entries (the "Retrieval")
3. Hand those log entries + the question to an LLM (the "Generation")
4. Print a plain-language answer

Run generate_logs.py and load_to_chroma.py first.

You need a free API key from Google AI Studio:
  1. Go to https://aistudio.google.com
  2. Sign in and click "Get API key" -> "Create API key"
  3. Set it as an environment variable: export GOOGLE_API_KEY=your-key-here

This script uses Google's Gemini API, since it has a genuinely free
tier (no credit card required for basic use) -- good for a practice
project like this.
"""

import logging
import os

import chromadb

# Load GOOGLE_API_KEY (and anything else) from a local .env file if present.
# Copy .env.example to .env and paste your key there.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # pip install python-dotenv  (or just export GOOGLE_API_KEY yourself)

# The google-genai SDK logs a "Direct use of automatic function calling (AFC)..."
# warning on every generate_content call. We pass no tools, so AFC is irrelevant
# here — quiet that logger down to errors only.
logging.getLogger("google_genai").setLevel(logging.ERROR)

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "pipeline_logs"
NUM_RESULTS = 300  # how many log entries to retrieve per question


def search_logs(question: str, n_results: int = NUM_RESULTS):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.query(query_texts=[question], n_results=n_results)

    # results["documents"][0] is the list of matching log sentences
    return results["documents"][0]


def call_llm(question: str, retrieved_logs: list[str]) -> str:
    """
    Sends the question + retrieved log context to Gemini and returns the answer.
    Requires: pip install google-genai
    And: export GOOGLE_API_KEY=your-key-here
    """
    from google import genai

    client = genai.Client()  # reads GOOGLE_API_KEY from environment

    context = "\n".join(f"- {log}" for log in retrieved_logs)

    prompt = f"""You are a helpful assistant that explains data pipeline health
to engineers based on log data. Answer the question using ONLY the log
entries below. If the logs don't contain enough information, say so.

Log entries:
{context}

Question: {question}

Answer clearly and concisely, referencing specific jobs/times where relevant."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    return response.text


def ask(question: str):
    print(f"\nQuestion: {question}")
    print("-" * 60)

    retrieved_logs = search_logs(question)

    print("Retrieved log entries:")
    for log in retrieved_logs:
        print(f"  • {log}")

    print("-" * 60)

    if not os.environ.get("GOOGLE_API_KEY"):
        print("(Skipping LLM call — set GOOGLE_API_KEY to see the generated answer)")
        return

    answer = call_llm(question, retrieved_logs)
    print(f"Answer:\n{answer}")


def run_interactive():
    """
    A simple loop so you can type your own questions live —
    this is the part you'd actually use in a demo.
    Type 'quit' or 'exit' to stop.
    """
    print("Pipeline Health Assistant")
    print("Ask me about job runs, failures, or performance. Type 'quit' to exit.\n")

    while True:
        question = input("> ").strip()
        if question.lower() in ("quit", "exit", ""):
            print("Goodbye!")
            break
        ask(question)


if __name__ == "__main__":
    run_interactive()