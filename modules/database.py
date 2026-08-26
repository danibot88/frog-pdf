
import sqlite3
from datetime import datetime

class LocalDatabase:
    """
    Class responsible for managing local SQLite database to persist 
    Projects (Clients), their status (active/inactive), and Chat Histories offline.
    """
    def __init__(self, db_path: str = "data/frog_pdf.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates required tables and ensures status column exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de Projetos / Clientes com campo de status (active / inactive)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT
            )
        ''')
        
        # Garante retrocompatibilidade caso a tabela já exista sem a coluna status
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'active'")
        except sqlite3.OperationalError:
            pass # A coluna já existe
        
        # Tabela de Histórico de Conversas vinculadas ao Projeto
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
        """Adds a new project or client locally as active by default."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO projects (name, status, created_at) VALUES (?, 'active', ?)", 
                           (name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        except Exception as e:
            print(f"Error adding project: {e}")
        finally:
            conn.close()

    def toggle_project_status(self, project_id: int, new_status: str):
        """Toggles a project's status between 'active' and 'inactive' (reference)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET status = ? WHERE id = ?", (new_status, project_id))
        conn.commit()
        conn.close()

    def get_projects(self, status: str = None) -> list:
        """Retrieves projects filtered by status ('active', 'inactive') or all if None."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT id, name, status FROM projects WHERE status = ? ORDER BY id DESC", (status,))
        else:
            cursor.execute("SELECT id, name, status FROM projects ORDER BY id DESC")
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