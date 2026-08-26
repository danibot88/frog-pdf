
import sqlite3
from datetime import datetime

class LocalDatabase:
    """
    Class responsible for managing local SQLite database to persist 
    Projects (Clients) and Chat Histories offline.
    """
    def __init__(self, db_path: str = "data/frog_pdf.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates required tables if they do not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_project(self, name: str):
        """Adds a new project or client locally."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO projects (name, created_at) VALUES (?, ?)", 
                           (name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        except Exception as e:
            print(f"Error adding project: {e}")
        finally:
            conn.close()

    def get_projects(self) -> list:
        """Retrieves all registered projects/clients."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM projects ORDER BY id DESC")
        projects = cursor.fetchall()
        conn.close()
        return projects

    def save_message(self, project_id: int, role: str, content: str):
        """Saves a chat message linked to a project."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chats (project_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                       (project_id, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def get_chat_history(self, project_id: int) -> list:
        """Retrieves chat history for a specific project."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM chats WHERE project_id = ? ORDER BY id ASC", (project_id,))
        messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        conn.close()
        return messages