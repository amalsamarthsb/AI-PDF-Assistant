import csv
import os
from datetime import datetime

LOG_FILE = "logs/rag_logs.csv"


def initialize_logger():
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow([
                "Timestamp",
                "Question",
                "Answer",
                "Retrieved Chunks",
                "Sources",
                "Response Time (sec)"
            ])


def log_interaction(
    question,
    answer,
    retrieved_chunks,
    sources,
    response_time
):

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question,
            answer,
            retrieved_chunks,
            ", ".join(sources),
            response_time
        ])