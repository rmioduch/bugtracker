"""
Uproszczona baza danych dla TaskMaster BugTracker
Bez skomplikowanych migracji - zawsze tworzy puste tabele od nowa
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from .entities import (
    Project, Task, TaskStatus, Comment, StatusHistory,
    User, Module, Version, Label, Attachment, TaskDependency,
    Watcher, Notification, SearchFilter, DashboardMetrics
)


class DatabaseManager:
    """Prosty menedżer bazy danych - jedna instancja dla całej aplikacji"""

    _instance = None
    _connection = None

    def __new__(cls, db_path: str = "taskmaster.db"):
        if cls._instance is None:
            print("🗄️ Tworzenie nowego DatabaseManager...")
            cls._instance = super().__new__(cls)
            cls._instance.db_path = db_path
            cls._instance._initialized = False
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """Pobierz połączenie z bazą danych"""
        if self._connection is None:
            print(f"🔌 Łączenie z bazą danych: {self.db_path}")
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row  # Dostęp do kolumn po nazwie

            # Włącz foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            print("✅ Połączenie z bazą danych nawiązane")

        return self._connection

    def close_connection(self):
        """Zamknij połączenie z bazą danych"""
        if self._connection:
            self._connection.close()
            self._connection = None
            print("🔐 Połączenie z bazą danych zamknięte")

    def initialize_database(self):
        """Utwórz wszystkie tabele od nowa"""
        if self._initialized:
            print("ℹ️ Baza danych już zainicjalizowana")
            return

        print("🚀 Inicjalizacja bazy danych - tworzenie tabel...")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Utwórz wszystkie tabele
            self._create_all_tables(cursor)

            # 2. Wstaw podstawowe dane
            self._insert_initial_data(cursor)

            # 3. Zapisz zmiany
            conn.commit()

            self._initialized = True
            print("✅ Baza danych zainicjalizowana pomyślnie!")

        except Exception as e:
            print(f"❌ Błąd inicjalizacji bazy danych: {e}")
            conn.rollback()
            raise

    def _create_all_tables(self, cursor: sqlite3.Cursor):
        """Utwórz wszystkie tabele"""

        print("📋 Tworzenie tabel...")

        # 1. USERS - użytkownicy systemu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'REPORTER',
                avatar_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        print("  ✅ Tabela users")

        # 2. PROJECTS - projekty
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Tabela projects")

        # 3. MODULES - moduły aplikacji
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                description TEXT,
                component_lead_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (component_lead_id) REFERENCES users(id)
            )
        """)
        print("  ✅ Tabela modules")

        # 4. VERSIONS - wersje aplikacji
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                release_date DATE,
                status TEXT DEFAULT 'PLANNED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Tabela versions")

        # 5. LABELS - etykiety
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT NOT NULL,
                description TEXT,
                is_system BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Tabela labels")

        # 6. TASK_STATUSES - statusy zadań
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_statuses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                color TEXT,
                sort_order INTEGER
            )
        """)
        print("  ✅ Tabela task_statuses")

        # 7. TASKS - główna tabela zadań/bugów
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status_id INTEGER NOT NULL DEFAULT 1,
                priority INTEGER DEFAULT 2,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Pola dla bug trackera
                issue_type TEXT DEFAULT 'TASK',
                severity INTEGER DEFAULT 3,
                reporter_id INTEGER,
                assignee_id INTEGER,
                module_id INTEGER,
                affected_version_id INTEGER,
                fix_version_id INTEGER,
                environment TEXT,
                steps_to_reproduce TEXT,
                expected_result TEXT,
                actual_result TEXT,
                stack_trace TEXT,
                resolution TEXT,
                resolution_notes TEXT,
                duplicate_of INTEGER,
                estimated_hours REAL,
                time_spent REAL,
                
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (status_id) REFERENCES task_statuses(id),
                FOREIGN KEY (reporter_id) REFERENCES users(id),
                FOREIGN KEY (assignee_id) REFERENCES users(id),
                FOREIGN KEY (module_id) REFERENCES modules(id),
                FOREIGN KEY (affected_version_id) REFERENCES versions(id),
                FOREIGN KEY (fix_version_id) REFERENCES versions(id)
            )
        """)
        print("  ✅ Tabela tasks")

        # 8. COMMENTS - komentarze do zadań
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                author_id INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
        """)
        print("  ✅ Tabela comments")

        # 9. STATUS_HISTORY - historia zmian statusów
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                old_status_id INTEGER,
                new_status_id INTEGER NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                changed_by INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (changed_by) REFERENCES users(id)
            )
        """)
        print("  ✅ Tabela status_history")

        # 10. TASK_LABELS - relacja zadania-etykiety
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_labels (
                task_id INTEGER,
                label_id INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (task_id, label_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE
            )
        """)
        print("  ✅ Tabela task_labels")

        # 11. ATTACHMENTS - załączniki
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                content_type TEXT,
                uploaded_by INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
        """)
        print("  ✅ Tabela attachments")

        # 12. WATCHERS - obserwatorzy zadań
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(task_id, user_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("  ✅ Tabela watchers")

        # 13. NOTIFICATIONS - powiadomienia
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_url TEXT,
                triggered_by_user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (triggered_by_user_id) REFERENCES users(id)
            )
        """)
        print("  ✅ Tabela notifications")

        # 14. TASK_DEPENDENCIES - zależności między zadaniami
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                depends_on_task_id INTEGER NOT NULL,
                dependency_type TEXT DEFAULT 'blocks',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        print("  ✅ Tabela task_dependencies")

        # Utwórz indeksy dla lepszej wydajności
        print("📇 Tworzenie indeksów...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_reporter ON tasks(reporter_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_module ON tasks(module_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_updated ON tasks(updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_comments_task ON comments(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        print("  ✅ Indeksy utworzone")

    def _insert_initial_data(self, cursor: sqlite3.Cursor):
        """Wstaw podstawowe dane do tabel"""

        print("📊 Wstawianie podstawowych danych...")

        # 1. STATUSY ZADAŃ
        statuses = [
            (1, "📋 To Do", "#6B7280", 1),
            (2, "🚀 In Progress", "#3B82F6", 2),
            (3, "👀 Review", "#F59E0B", 3),
            (4, "🔒 Blocked", "#EF4444", 4),
            (5, "✅ Done", "#10B981", 5),
            (6, "🔍 Triaged", "#9CA3AF", 6),
            (7, "👀 Code Review", "#8B5CF6", 7),
            (8, "🧪 Testing", "#06B6D4", 8),
            (9, "✅ Verification", "#10B981", 9),
            (10, "🔄 Reopened", "#F59E0B", 10)
        ]

        for status_id, name, color, sort_order in statuses:
            cursor.execute("""
                INSERT OR IGNORE INTO task_statuses (id, name, color, sort_order)
                VALUES (?, ?, ?, ?)
            """, (status_id, name, color, sort_order))
        print("  ✅ Statusy zadań")

        # 2. DOMYŚLNY PROJEKT
        cursor.execute("""
            INSERT OR IGNORE INTO projects (name, description)
            VALUES (?, ?)
        """, ("Money Mentor AI", "Główny projekt aplikacji Money Mentor AI"))
        print("  ✅ Domyślny projekt")

        # 3. MODUŁY MONEY MENTOR AI
        modules_data = [
            ('CORE', '🏗️ Core System', 'Podstawowa funkcjonalność systemu'),
            ('TRADING', '📈 Trading Module', 'Silnik tradingowy i wykonywanie transakcji'),
            ('BROKER', '🔗 Broker Integration', 'Integracje z brokerami'),
            ('STRATEGY', '🧠 Strategy Engine', 'Strategie tradingowe'),
            ('RISK', '⚠️ Risk Management', 'Zarządzanie ryzykiem'),
            ('PORTFOLIO', '💼 Portfolio Management', 'Zarządzanie portfelem'),
            ('ANALYSIS', '📊 Technical Analysis', 'Analiza techniczna i wskaźniki'),
            ('DATA', '💾 Data Management', 'Obsługa danych rynkowych'),
            ('UI', '🎨 User Interface', 'Interfejs użytkownika'),
            ('DB', '🗄️ Database', 'Operacje bazodanowe'),
            ('API', '🔌 API Integrations', 'Integracje z zewnętrznymi API'),
            ('REPORTING', '📋 Reports & Visualization', 'Raporty i wizualizacje'),
            ('SECURITY', '🔒 Security', 'Funkcje bezpieczeństwa'),
            ('PERFORMANCE', '⚡ Performance', 'Optymalizacja wydajności'),
            ('TESTING', '🧪 Testing Framework', 'Infrastruktura testowa')
        ]

        for name, display_name, description in modules_data:
            cursor.execute("""
                INSERT OR IGNORE INTO modules (name, display_name, description)
                VALUES (?, ?, ?)
            """, (name, display_name, description))
        print("  ✅ Moduły Money Mentor AI")

        # 4. DOMYŚLNE ETYKIETY
        labels_data = [
            ('performance-critical', '#FF4444', 'Krytyczne dla wydajności'),
            ('customer-reported', '#4444FF', 'Zgłoszone przez klienta'),
            ('regression', '#FF8800', 'Regresja - wcześniej działało'),
            ('hotfix-candidate', '#FF0000', 'Kandydat do hotfixa'),
            ('breaking-change', '#8800FF', 'Zmiana łamiąca kompatybilność'),
            ('easy-fix', '#88FF00', 'Łatwa poprawka dla nowych programistów')
        ]

        for name, color, description in labels_data:
            cursor.execute("""
                INSERT OR IGNORE INTO labels (name, color, description, is_system)
                VALUES (?, ?, ?, 1)
            """, (name, color, description))
        print("  ✅ Domyślne etykiety")

        # 5. WERSJE
        cursor.execute("""
            INSERT OR IGNORE INTO versions (name, description, status)
            VALUES 
                ('v1.0.0', 'Pierwsza wersja produkcyjna', 'RELEASED'),
                ('v1.1.0', 'Poprawki i ulepszenia', 'PLANNED'),
                ('v2.0.0', 'Duża aktualizacja funkcji', 'PLANNED')
        """)
        print("  ✅ Wersje")

    # ==================== OPERACJE NA UŻYTKOWNIKACH ====================

    def create_user(self, user: User) -> int:
        """Utwórz nowego użytkownika"""
        print(f"👤 Tworzenie użytkownika: {user.username}")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, email, full_name, role, avatar_url, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user.username, user.email, user.full_name, user.role,
                  user.avatar_url, user.is_active))

            conn.commit()
            user_id = cursor.lastrowid
            print(f"  ✅ Użytkownik utworzony z ID: {user_id}")
            return user_id

        except sqlite3.IntegrityError as e:
            print(f"  ❌ Błąd: użytkownik {user.username} już istnieje")
            raise ValueError(f"Użytkownik {user.username} już istnieje")
        except Exception as e:
            print(f"  ❌ Błąd tworzenia użytkownika: {e}")
            conn.rollback()
            raise

    def get_all_users(self, active_only: bool = True) -> List[User]:
        """Pobierz wszystkich użytkowników"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY username")
        else:
            cursor.execute("SELECT * FROM users ORDER BY username")

        rows = cursor.fetchall()
        users = []

        for row in rows:
            user = User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                full_name=row['full_name'],
                role=row['role'],
                avatar_url=row['avatar_url'],
                is_active=bool(row['is_active']),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None
            )
            users.append(user)

        print(f"👥 Pobrano {len(users)} użytkowników")
        return users

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Pobierz użytkownika po ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                full_name=row['full_name'],
                role=row['role'],
                avatar_url=row['avatar_url'],
                is_active=bool(row['is_active']),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None
            )
        return None

    def update_user(self, user: User):
        """Aktualizuj użytkownika"""
        print(f"✏️ Aktualizacja użytkownika: {user.username}")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users SET 
                username = ?, email = ?, full_name = ?, role = ?, 
                avatar_url = ?, is_active = ?
            WHERE id = ?
        """, (user.username, user.email, user.full_name, user.role,
              user.avatar_url, user.is_active, user.id))

        conn.commit()
        print(f"  ✅ Użytkownik zaktualizowany")

    # ==================== OPERACJE NA PROJEKTACH ====================

    def create_project(self, project: Project) -> int:
        """Utwórz nowy projekt"""
        print(f"📁 Tworzenie projektu: {project.name}")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO projects (name, description) VALUES (?, ?)",
            (project.name, project.description)
        )

        conn.commit()
        project_id = cursor.lastrowid
        print(f"  ✅ Projekt utworzony z ID: {project_id}")
        return project_id

    def get_all_projects(self) -> List[Project]:
        """Pobierz wszystkie projekty"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects ORDER BY name")
        rows = cursor.fetchall()

        projects = []
        for row in rows:
            project = Project(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
            projects.append(project)

        print(f"📁 Pobrano {len(projects)} projektów")
        return projects

    def update_project(self, project: Project):
        """Aktualizuj projekt"""
        print(f"✏️ Aktualizacja projektu: {project.name}")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE projects SET name = ?, description = ? WHERE id = ?",
            (project.name, project.description, project.id)
        )
        conn.commit()
        print(f"  ✅ Projekt zaktualizowany")

    def delete_project(self, project_id: int):
        """Usuń projekt i wszystkie jego zadania"""
        print(f"🗑️ Usuwanie projektu ID: {project_id}")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Usuń wszystkie zadania i powiązane dane
        cursor.execute("DELETE FROM comments WHERE task_id IN (SELECT id FROM tasks WHERE project_id = ?)", (project_id,))
        cursor.execute("DELETE FROM status_history WHERE task_id IN (SELECT id FROM tasks WHERE project_id = ?)", (project_id,))
        cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))

        conn.commit()
        print(f"  ✅ Projekt usunięty")

    # ==================== OPERACJE NA ZADANIACH ====================

    def create_task(self, task: Task) -> int:
        """Utwórz nowe zadanie"""
        print(f"📋 Tworzenie zadania: {task.title}")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tasks (
                project_id, title, description, status_id, priority,
                issue_type, severity, reporter_id, assignee_id, module_id,
                affected_version_id, fix_version_id, environment,
                steps_to_reproduce, expected_result, actual_result,
                stack_trace, estimated_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.project_id, task.title, task.description, task.status_id, task.priority,
            task.issue_type, task.severity, task.reporter_id, task.assignee_id, task.module_id,
            task.affected_version_id, task.fix_version_id, task.environment,
            task.steps_to_reproduce, task.expected_result, task.actual_result,
            task.stack_trace, task.estimated_hours
        ))

        task_id = cursor.lastrowid

        # Zapisz historię statusu
        cursor.execute("""
            INSERT INTO status_history (task_id, old_status_id, new_status_id, changed_by)
            VALUES (?, ?, ?, ?)
        """, (task_id, None, task.status_id, task.reporter_id))

        conn.commit()
        print(f"  ✅ Zadanie utworzone z ID: {task_id}")
        return task_id

    def update_task(self, task: Task):
        """Aktualizuj zadanie"""
        print(f"✏️ Aktualizacja zadania: {task.title}")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tasks SET 
                title = ?, description = ?, status_id = ?, priority = ?,
                issue_type = ?, severity = ?, assignee_id = ?, module_id = ?,
                affected_version_id = ?, fix_version_id = ?, environment = ?,
                steps_to_reproduce = ?, expected_result = ?, actual_result = ?,
                stack_trace = ?, resolution = ?, resolution_notes = ?,
                estimated_hours = ?, time_spent = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            task.title, task.description, task.status_id, task.priority,
            task.issue_type, task.severity, task.assignee_id, task.module_id,
            task.affected_version_id, task.fix_version_id, task.environment,
            task.steps_to_reproduce, task.expected_result, task.actual_result,
            task.stack_trace, task.resolution, task.resolution_notes,
            task.estimated_hours, task.time_spent, task.id
        ))

        conn.commit()
        print(f"  ✅ Zadanie zaktualizowane")

    def delete_task(self, task_id: int):
        """Usuń zadanie"""
        print(f"🗑️ Usuwanie zadania ID: {task_id}")

        conn = self.get_connection()
        cursor = conn.cursor()

        # CASCADE usuwa powiązane komentarze i historię
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        print(f"  ✅ Zadanie usunięte")

    def get_all_statuses(self) -> List[TaskStatus]:
        """Pobierz wszystkie statusy zadań"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM task_statuses ORDER BY sort_order")
        rows = cursor.fetchall()

        statuses = []
        for row in rows:
            status = TaskStatus(
                id=row['id'],
                name=row['name'],
                color=row['color'],
                sort_order=row['sort_order']
            )
            statuses.append(status)

        return statuses

    # ==================== OPERACJE NA MODUŁACH ====================

    def get_all_modules(self, active_only: bool = True) -> List[Module]:
        """Pobierz wszystkie moduły"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute("""
                SELECT m.*, u.full_name as lead_name 
                FROM modules m 
                LEFT JOIN users u ON m.component_lead_id = u.id 
                WHERE m.is_active = 1 
                ORDER BY m.display_name
            """)
        else:
            cursor.execute("""
                SELECT m.*, u.full_name as lead_name 
                FROM modules m 
                LEFT JOIN users u ON m.component_lead_id = u.id 
                ORDER BY m.display_name
            """)

        rows = cursor.fetchall()
        modules = []

        for row in rows:
            module = Module(
                id=row['id'],
                name=row['name'],
                display_name=row['display_name'],
                description=row['description'],
                component_lead_id=row['component_lead_id'],
                component_lead_name=row['lead_name'],
                is_active=bool(row['is_active']),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
            modules.append(module)

        return modules

    # ==================== OPERACJE NA WERSJACH ====================

    def get_all_versions(self) -> List[Version]:
        """Pobierz wszystkie wersje"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM versions ORDER BY created_at DESC")
        rows = cursor.fetchall()

        versions = []
        for row in rows:
            version = Version(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                release_date=datetime.fromisoformat(row['release_date']) if row['release_date'] else None,
                status=row['status'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
            versions.append(version)

        return versions

    # ==================== OPERACJE NA ETYKIETACH ====================

    def get_all_labels(self) -> List[Label]:
        """Pobierz wszystkie etykiety"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM labels ORDER BY name")
        rows = cursor.fetchall()

        labels = []
        for row in rows:
            label = Label(
                id=row['id'],
                name=row['name'],
                color=row['color'],
                description=row['description'],
                is_system=bool(row['is_system']),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
            labels.append(label)

        return labels

    def create_label(self, label: Label) -> int:
        """Utwórz nową etykietę"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO labels (name, color, description, is_system)
            VALUES (?, ?, ?, ?)
        """, (label.name, label.color, label.description, label.is_system))

        conn.commit()
        return cursor.lastrowid

    def get_task_labels(self, task_id: int) -> List[Label]:
        """Pobierz etykiety dla zadania"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT l.* FROM labels l
            JOIN task_labels tl ON l.id = tl.label_id
            WHERE tl.task_id = ?
            ORDER BY l.name
        """, (task_id,))

        rows = cursor.fetchall()
        labels = []

        for row in rows:
            label = Label(
                id=row['id'],
                name=row['name'],
                color=row['color'],
                description=row['description'],
                is_system=bool(row['is_system']),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
            labels.append(label)

        return labels

    def add_label_to_task(self, task_id: int, label_id: int):
        """Dodaj etykietę do zadania"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO task_labels (task_id, label_id)
            VALUES (?, ?)
        """, (task_id, label_id))

        conn.commit()

    def remove_label_from_task(self, task_id: int, label_id: int):
        """Usuń etykietę z zadania"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM task_labels WHERE task_id = ? AND label_id = ?
        """, (task_id, label_id))

        conn.commit()

    # ==================== OPERACJE NA KOMENTARZACH ====================

    def add_comment(self, comment: Comment) -> int:
        """Dodaj komentarz do zadania"""
        print(f"💬 Dodawanie komentarza do zadania ID: {comment.task_id}")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO comments (task_id, content, author_id)
            VALUES (?, ?, ?)
        """, (comment.task_id, comment.content, comment.author_id))

        conn.commit()
        comment_id = cursor.lastrowid
        print(f"  ✅ Komentarz dodany z ID: {comment_id}")
        return comment_id

    def get_task_comments(self, task_id: int) -> List[Comment]:
        """Pobierz komentarze dla zadania"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.*, u.full_name as author_name
            FROM comments c
            LEFT JOIN users u ON c.author_id = u.id
            WHERE c.task_id = ?
            ORDER BY c.created_at DESC
        """, (task_id,))

        rows = cursor.fetchall()
        comments = []

        for row in rows:
            comment = Comment(
                id=row['id'],
                task_id=row['task_id'],
                content=row['content'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                author_id=row['author_id'],
                author_name=row['author_name']
            )
            comments.append(comment)

        return comments

    # ==================== WYSZUKIWANIE I FILTROWANIE ====================

    def get_enhanced_tasks_by_filter(self, search_filter: SearchFilter) -> List[Task]:
        """Pobierz zadania z zaawansowanymi filtrami"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Podstawowe zapytanie
        base_query = """
            SELECT 
                t.*,
                p.name as project_name,
                ts.name as status_name,
                rep.full_name as reporter_name,
                ass.full_name as assignee_name,
                m.display_name as module_name,
                av.name as affected_version_name,
                fv.name as fix_version_name,
                (SELECT COUNT(*) FROM comments WHERE task_id = t.id) as comments_count,
                (SELECT COUNT(*) FROM attachments WHERE task_id = t.id) as attachments_count
            FROM tasks t
            JOIN projects p ON t.project_id = p.id
            JOIN task_statuses ts ON t.status_id = ts.id
            LEFT JOIN users rep ON t.reporter_id = rep.id
            LEFT JOIN users ass ON t.assignee_id = ass.id
            LEFT JOIN modules m ON t.module_id = m.id
            LEFT JOIN versions av ON t.affected_version_id = av.id
            LEFT JOIN versions fv ON t.fix_version_id = fv.id
        """

        # Buduj warunki WHERE
        where_clauses = []
        params = []

        if search_filter.query:
            where_clauses.append("(t.title LIKE ? OR t.description LIKE ?)")
            query_param = f"%{search_filter.query}%"
            params.extend([query_param, query_param])

        if search_filter.project_id:
            where_clauses.append("t.project_id = ?")
            params.append(search_filter.project_id)

        if search_filter.issue_type:
            where_clauses.append("t.issue_type = ?")
            params.append(search_filter.issue_type)

        if search_filter.status_id:
            where_clauses.append("t.status_id = ?")
            params.append(search_filter.status_id)

        if search_filter.priority:
            where_clauses.append("t.priority = ?")
            params.append(search_filter.priority)

        if search_filter.assignee_id:
            where_clauses.append("t.assignee_id = ?")
            params.append(search_filter.assignee_id)

        if search_filter.module_id:
            where_clauses.append("t.module_id = ?")
            params.append(search_filter.module_id)

        # Zbuduj finalne zapytanie
        if where_clauses:
            query = base_query + " WHERE " + " AND ".join(where_clauses)
        else:
            query = base_query

        query += " ORDER BY t.updated_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            task = Task(
                id=row['id'],
                project_id=row['project_id'],
                title=row['title'],
                description=row['description'],
                status_id=row['status_id'],
                priority=row['priority'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                project_name=row['project_name'],
                status_name=row['status_name'],

                # Pola bug trackera
                issue_type=row['issue_type'],
                severity=row['severity'],
                reporter_id=row['reporter_id'],
                reporter_name=row['reporter_name'],
                assignee_id=row['assignee_id'],
                assignee_name=row['assignee_name'],
                module_id=row['module_id'],
                module_name=row['module_name'],
                affected_version_id=row['affected_version_id'],
                affected_version_name=row['affected_version_name'],
                fix_version_id=row['fix_version_id'],
                fix_version_name=row['fix_version_name'],
                environment=row['environment'],
                steps_to_reproduce=row['steps_to_reproduce'],
                expected_result=row['expected_result'],
                actual_result=row['actual_result'],
                stack_trace=row['stack_trace'],
                resolution=row['resolution'],
                resolution_notes=row['resolution_notes'],
                duplicate_of=row['duplicate_of'],
                estimated_hours=row['estimated_hours'],
                time_spent=row['time_spent'],

                # Liczniki
                comments_count=row['comments_count'],
                attachments_count=row['attachments_count']
            )

            # Wczytaj etykiety
            task.labels = self.get_task_labels(task.id)
            tasks.append(task)

        print(f"🔍 Znaleziono {len(tasks)} zadań")
        return tasks

    # ==================== DASHBOARD I METRYKI ====================

    def get_dashboard_metrics(self, user_id: Optional[int] = None) -> DashboardMetrics:
        """Pobierz metryki dla dashboardu"""
        conn = self.get_connection()
        cursor = conn.cursor()

        metrics = DashboardMetrics()

        # Całkowita liczba zadań
        cursor.execute("SELECT COUNT(*) FROM tasks")
        metrics.total_issues = cursor.fetchone()[0]

        # Otwarte vs zamknięte zadania
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN ts.name IN ('📋 To Do', '🚀 In Progress', '👀 Review', '🔒 Blocked', '🔍 Triaged', '👀 Code Review', '🧪 Testing', '🔄 Reopened') THEN 1 END) as open_count,
                COUNT(CASE WHEN ts.name IN ('✅ Done', '✅ Verification') THEN 1 END) as closed_count
            FROM tasks t
            JOIN task_statuses ts ON t.status_id = ts.id
        """)
        result = cursor.fetchone()
        metrics.open_issues = result[0] or 0
        metrics.closed_issues = result[1] or 0

        # Krytyczne bugi
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE issue_type = 'BUG' AND priority = 1
        """)
        metrics.critical_bugs = cursor.fetchone()[0]

        # Moje przypisane (jeśli podano user_id)
        if user_id:
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE assignee_id = ? AND status_id IN (1, 2, 3, 4, 6, 7, 8, 10)
            """, (user_id,))
            metrics.my_assigned = cursor.fetchone()[0]

        # Zadania według modułów
        cursor.execute("""
            SELECT COALESCE(m.display_name, 'Nie przypisano'), COUNT(t.id) as count
            FROM modules m
            LEFT JOIN tasks t ON m.id = t.module_id
            GROUP BY m.id, m.display_name
            UNION
            SELECT 'Nie przypisano', COUNT(*)
            FROM tasks
            WHERE module_id IS NULL
            ORDER BY count DESC
        """)
        metrics.issues_by_module = {row[0]: row[1] for row in cursor.fetchall()}

        # Zadania według statusów
        cursor.execute("""
            SELECT ts.name, COUNT(t.id) as count
            FROM task_statuses ts
            LEFT JOIN tasks t ON ts.id = t.status_id
            GROUP BY ts.id, ts.name
            ORDER BY count DESC
        """)
        metrics.issues_by_status = {row[0]: row[1] for row in cursor.fetchall()}

        print(f"📊 Pobrano metryki: {metrics.total_issues} zadań, {metrics.open_issues} otwartych")
        return metrics

    def update_task_status(self, task_id: int, new_status_id: int):
        """Aktualizuj status zadania i zapisz historię"""
        print(f"🔄 Zmiana statusu zadania {task_id} na {new_status_id}")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Pobierz obecny status
        cursor.execute("SELECT status_id FROM tasks WHERE id = ?", (task_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Zadanie {task_id} nie istnieje")

        old_status_id = result[0]

        # Aktualizuj status
        cursor.execute("""
            UPDATE tasks SET status_id = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (new_status_id, task_id))

        # Zapisz historię
        cursor.execute("""
            INSERT INTO status_history (task_id, old_status_id, new_status_id)
            VALUES (?, ?, ?)
        """, (task_id, old_status_id, new_status_id))

        conn.commit()
        print(f"  ✅ Status zmieniony z {old_status_id} na {new_status_id}")

    # ==================== ZAŁĄCZNIKI ====================

    def create_attachment(self, attachment: Attachment) -> int:
        """Dodaj załącznik do zadania"""
        print(f"📎 Dodawanie załącznika: {attachment.original_filename}")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attachments (
                task_id, filename, original_filename, file_path, 
                file_size, content_type, uploaded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            attachment.task_id, attachment.filename, attachment.original_filename,
            attachment.file_path, attachment.file_size, attachment.content_type,
            attachment.uploaded_by
        ))

        conn.commit()
        attachment_id = cursor.lastrowid
        print(f"  ✅ Załącznik dodany z ID: {attachment_id}")
        return attachment_id

    def get_task_attachments(self, task_id: int) -> List[Attachment]:
        """Pobierz załączniki dla zadania"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, u.full_name as uploaded_by_name
            FROM attachments a
            LEFT JOIN users u ON a.uploaded_by = u.id
            WHERE a.task_id = ?
            ORDER BY a.uploaded_at DESC
        """, (task_id,))

        rows = cursor.fetchall()
        attachments = []

        for row in rows:
            attachment = Attachment(
                id=row['id'],
                task_id=row['task_id'],
                filename=row['filename'],
                original_filename=row['original_filename'],
                file_path=row['file_path'],
                file_size=row['file_size'],
                content_type=row['content_type'],
                uploaded_by=row['uploaded_by'],
                uploaded_by_name=row['uploaded_by_name'],
                uploaded_at=datetime.fromisoformat(row['uploaded_at']) if row['uploaded_at'] else None
            )
            attachments.append(attachment)

        return attachments

    def delete_attachment(self, attachment_id: int):
        """Delete attachment from database - POPRAWIONA WERSJA"""
        print(f"🗑️ Deleting attachment ID: {attachment_id}")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Najpierw pobierz ścieżkę pliku dla ewentualnego usunięcia
        cursor.execute("SELECT file_path FROM attachments WHERE id = ?", (attachment_id,))
        result = cursor.fetchone()

        if result:
            file_path = result[0]

            # Usuń z bazy danych
            cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            conn.commit()
            print(f"  ✅ Attachment deleted from database")

            return file_path
        else:
            print(f"  ⚠️ Attachment {attachment_id} not found")
            return None

    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Get attachment by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, u.full_name as uploaded_by_name
            FROM attachments a
            LEFT JOIN users u ON a.uploaded_by = u.id
            WHERE a.id = ?
        """, (attachment_id,))

        row = cursor.fetchone()
        if row:
            return Attachment(
                id=row['id'],
                task_id=row['task_id'],
                filename=row['filename'],
                original_filename=row['original_filename'],
                file_path=row['file_path'],
                file_size=row['file_size'],
                content_type=row['content_type'],
                uploaded_by=row['uploaded_by'],
                uploaded_by_name=row['uploaded_by_name'],
                uploaded_at=datetime.fromisoformat(row['uploaded_at']) if row['uploaded_at'] else None
            )
        return None

    def get_attachment_stats_for_task(self, task_id: int) -> Dict:
        """Get attachment statistics for a task"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                SUM(file_size) as total_size,
                AVG(file_size) as avg_size,
                MAX(file_size) as max_size
            FROM attachments 
            WHERE task_id = ?
        """, (task_id,))

        result = cursor.fetchone()

        return {
            'count': result[0] or 0,
            'total_size': result[1] or 0,
            'average_size': result[2] or 0,
            'max_size': result[3] or 0
        }