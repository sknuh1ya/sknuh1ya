
import json
import sqlite3
from datetime import datetime


def init_db(db_path):
    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_type TEXT NOT NULL,
            analysis_date TEXT NOT NULL,
            document_status TEXT NOT NULL,
            overall_status TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_application(
    db_path,
    application_type,
    report,
):
    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        INSERT INTO applications (
            application_type,
            analysis_date,
            document_status,
            overall_status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            application_type,
            datetime.now().isoformat(
                timespec="seconds"
            ),
            json.dumps(report["checklist"]),
            report["overall_status"],
        ),
    )

    connection.commit()
    connection.close()
