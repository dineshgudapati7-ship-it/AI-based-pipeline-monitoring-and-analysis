"""
load_to_chroma.py
Loads the synthetic pipeline_logs.csv into a local Chroma collection
so we can search log entries by meaning, not just exact keywords.

Run generate_logs.py first to create pipeline_logs.csv.
"""

import csv
import chromadb

CSV_PATH = "pipeline_logs.csv"
CHROMA_PATH = "./chroma_db"  # this creates a local folder — no cloud, nothing leaves your laptop
COLLECTION_NAME = "pipeline_logs"


def row_to_document(row: dict) -> str:
    """
    Turn one CSV row into a natural-language sentence.
    This is the text that actually gets embedded and searched —
    the more descriptive it is, the better the search results.
    """
    if row["status"] == "SUCCESS":
        detail = "completed successfully with no errors."
    else:
        detail = f"ended with status {row['status']}. Details: {row['error_message']}"

    return (
        f"Job '{row['job_name']}' ran on {row['run_timestamp']}. "
        f"It {detail} "
        f"Duration: {row['duration_minutes']} minutes. "
        f"Rows processed: {row['rows_processed']}."
    )


def load_logs_into_chroma():
    # Read the CSV
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))

    # Set up a local, on-disk Chroma client (no server, no API key needed)
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Start fresh each time we load, so re-running this script doesn't duplicate data
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    documents = [row_to_document(row) for row in rows]
    ids = [row["run_id"] for row in rows]
    metadatas = [
        {
            "job_name": row["job_name"],
            "status": row["status"],
            "run_timestamp": row["run_timestamp"],
        }
        for row in rows
    ]

    # Chroma handles the embedding automatically with a default local model
    collection.add(documents=documents, ids=ids, metadatas=metadatas)

    print(f"Loaded {len(documents)} log entries into Chroma collection '{COLLECTION_NAME}'")
    print(f"Stored at: {CHROMA_PATH}")

    return collection


if __name__ == "__main__":
    load_logs_into_chroma()