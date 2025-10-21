#!/usr/bin/env python3
"""
Advanced Terminal-Based Task Management System
Features: SQLite DB, ML-based priority suggestions, analytics, export/import
"""

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os
import sys
from collections import defaultdict
import math

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Database:
    """Handles all database operations"""
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Tasks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority INTEGER DEFAULT 3,
                status TEXT DEFAULT 'pending',
                deadline TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                estimated_hours REAL,
                actual_hours REAL
            )
        ''')
        
        # Task history for ML training
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                category TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                days_to_deadline INTEGER,
                completion_time_hours REAL,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        # Tags table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                tag TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        self.conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor"""
        return self.cursor.execute(query, params)
    
    def commit(self):
        """Commit changes"""
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

class TaskManager:
    """Main task management system"""
    
    def __init__(self):
        self.db = Database()
        self.ml_model = PriorityPredictor(self.db)
    
    def add_task(self, title: str, description: str = "", category: str = "general",
                 priority: int = 3, deadline: Optional[str] = None, 
                 estimated_hours: float = 0, tags: List[str] = None):
        """Add a new task"""
        self.db.execute('''
            INSERT INTO tasks (title, description, category, priority, deadline, estimated_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, category, priority, deadline, estimated_hours))
        
        task_id = self.db.cursor.lastrowid
        
        # Add tags
        if tags:
            for tag in tags:
                self.db.execute('INSERT INTO tags (task_id, tag) VALUES (?, ?)', 
                              (task_id, tag.strip()))
        
        self.db.commit()
        return task_id
    
    def get_tasks(self, status: str = None, category: str = None) -> List[Dict]:
        """Retrieve tasks with filters"""
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        query += ' ORDER BY priority ASC, deadline ASC'
        
        self.db.execute(query, tuple(params))
        tasks = []
        
        for row in self.db.cursor.fetchall():
            task = {
                'id': row[0], 'title': row[1], 'description': row[2],
                'category': row[3], 'priority': row[4], 'status': row[5],
                'deadline': row[6], 'created_at': row[7], 'completed_at': row[8],
                'estimated_hours': row[9], 'actual_hours': row[10]
            }
            
            # Get tags
            self.db.execute('SELECT tag FROM tags WHERE task_id = ?', (task['id'],))
            task['tags'] = [tag[0] for tag in self.db.cursor.fetchall()]
            
            tasks.append(task)
        
        return tasks
    
    def update_task(self, task_id: int, **kwargs):
        """Update task fields"""
        allowed_fields = ['title', 'description', 'category', 'priority', 
                         'status', 'deadline', 'estimated_hours', 'actual_hours']
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f'{field} = ?')
                values.append(value)
        
        if updates:
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
            self.db.execute(query, tuple(values))
            self.db.commit()
    
    def complete_task(self, task_id: int, actual_hours: float = None):
        """Mark task as completed and log to history"""
        # Get task details
        self.db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = self.db.cursor.fetchone()
        
        if task:
            completed_at = datetime.now().isoformat()
            self.db.execute('''
                UPDATE tasks 
                SET status = 'completed', completed_at = ?, actual_hours = ?
                WHERE id = ?
            ''', (completed_at, actual_hours, task_id))
            
            # Log to history for ML
            created = datetime.fromisoformat(task[7])
            completed = datetime.fromisoformat(completed_at)
            completion_time = (completed - created).total_seconds() / 3600
            
            days_to_deadline = None
            if task[6]:  # deadline exists
                deadline = datetime.fromisoformat(task[6])
                days_to_deadline = (deadline - created).days
            
            self.db.execute('''
                INSERT INTO task_history 
                (task_id, category, estimated_hours, actual_hours, 
                 days_to_deadline, completion_time_hours)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (task_id, task[3], task[9], actual_hours, 
                  days_to_deadline, completion_time))
            
            self.db.commit()
    
    def delete_task(self, task_id: int):
        """Delete a task and its tags"""
        self.db.execute('DELETE FROM tags WHERE task_id = ?', (task_id,))
        self.db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.db.commit()
    
    def get_statistics(self) -> Dict:
        """Generate task statistics"""
        stats = {}
        
        # Total tasks by status
        self.db.execute('SELECT status, COUNT(*) FROM tasks GROUP BY status')
        stats['by_status'] = dict(self.db.cursor.fetchall())
        
        # Tasks by category
        self.db.execute('SELECT category, COUNT(*) FROM tasks GROUP BY category')
        stats['by_category'] = dict(self.db.cursor.fetchall())
        
        # Average completion time
        self.db.execute('''
            SELECT AVG(completion_time_hours) 
            FROM task_history 
            WHERE completion_time_hours IS NOT NULL
        ''')
        avg_completion = self.db.cursor.fetchone()[0]
        stats['avg_completion_hours'] = round(avg_completion, 2) if avg_completion else 0
        
        # Overdue tasks
        today = datetime.now().isoformat()
        self.db.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE deadline < ? AND status != 'completed'
        ''', (today,))
        stats['overdue'] = self.db.cursor.fetchone()[0]
        
        return stats
    
    def export_tasks(self, filename: str, format: str = 'json'):
        """Export tasks to JSON or CSV"""
        tasks = self.get_tasks()
        
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(tasks, f, indent=2)
        
        elif format == 'csv':
            with open(filename, 'w', newline='') as f:
                if tasks:
                    writer = csv.DictWriter(f, fieldnames=tasks[0].keys())
                    writer.writeheader()
                    writer.writerows(tasks)
    
    def import_tasks(self, filename: str):
        """Import tasks from JSON file"""
        with open(filename, 'r') as f:
            tasks = json.load(f)
        
        for task in tasks:
            tags = task.pop('tags', [])
            task.pop('id', None)  # Remove ID to auto-generate new ones
            task.pop('created_at', None)
            task.pop('completed_at', None)
            
            self.add_task(
                title=task['title'],
                description=task.get('description', ''),
                category=task.get('category', 'general'),
                priority=task.get('priority', 3),
                deadline=task.get('deadline'),
                estimated_hours=task.get('estimated_hours', 0),
                tags=tags
            )

class PriorityPredictor:
    """ML-based priority suggestion system"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def suggest_priority(self, category: str, estimated_hours: float, 
                        deadline_days: Optional[int]) -> int:
        """Suggest priority based on historical data"""
        # Get historical data for similar tasks
        self.db.execute('''
            SELECT estimated_hours, days_to_deadline, completion_time_hours
            FROM task_history
            WHERE category = ?
        ''', (category,))
        
        history = self.db.cursor.fetchall()
        
        if not history:
            # No history, use simple heuristic
            return self._heuristic_priority(estimated_hours, deadline_days)
        
        # Calculate weighted score based on historical patterns
        urgency_score = 0
        complexity_score = 0
        
        for hist_est, hist_deadline, hist_completion in history:
            if hist_est and estimated_hours:
                # Compare estimated hours
                complexity_score += abs(hist_est - estimated_hours)
            
            if hist_deadline and deadline_days:
                # Compare deadline urgency
                urgency_score += abs(hist_deadline - deadline_days)
        
        # Normalize scores
        if history:
            complexity_score /= len(history)
            urgency_score /= len(history)
        
        # Combine scores for priority (1-5, where 1 is highest)
        if deadline_days and deadline_days <= 7:
            priority = 1
        elif deadline_days and deadline_days <= 14:
            priority = 2
        elif estimated_hours > 20:
            priority = 2
        elif estimated_hours > 10:
            priority = 3
        else:
            priority = 4
        
        return max(1, min(5, priority))
    
    def _heuristic_priority(self, estimated_hours: float, 
                           deadline_days: Optional[int]) -> int:
        """Simple heuristic when no historical data exists"""
        if deadline_days and deadline_days <= 3:
            return 1
        elif deadline_days and deadline_days <= 7:
            return 2
        elif estimated_hours > 15:
            return 2
        elif estimated_hours > 5:
            return 3
        else:
            return 4

class UI:
    """Terminal UI handler"""
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(text: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")
    
    @staticmethod
    def print_task(task: Dict, index: int = None):
        """Print a single task"""
        prefix = f"{index}. " if index else ""
        
        # Priority color
        priority_colors = {1: Colors.FAIL, 2: Colors.WARNING, 
                          3: Colors.CYAN, 4: Colors.GREEN, 5: Colors.BLUE}
        color = priority_colors.get(task['priority'], Colors.ENDC)
        
        print(f"{color}{Colors.BOLD}{prefix}{task['title']}{Colors.ENDC}")
        print(f"  ID: {task['id']} | Category: {task['category']} | "
              f"Priority: {task['priority']} | Status: {task['status']}")
        
        if task['description']:
            print(f"  Description: {task['description']}")
        
        if task['deadline']:
            deadline = datetime.fromisoformat(task['deadline'])
            days_left = (deadline - datetime.now()).days
            deadline_str = deadline.strftime('%Y-%m-%d')
            
            if days_left < 0:
                print(f"  {Colors.FAIL}⚠ OVERDUE: {deadline_str}{Colors.ENDC}")
            elif days_left <= 3:
                print(f"  {Colors.WARNING}⏰ Deadline: {deadline_str} ({days_left} days){Colors.ENDC}")
            else:
                print(f"  📅 Deadline: {deadline_str} ({days_left} days)")
        
        if task['tags']:
            print(f"  Tags: {', '.join(task['tags'])}")
        
        print()
    
    @staticmethod
    def print_statistics(stats: Dict):
        """Print statistics"""
        UI.print_header("📊 TASK STATISTICS")
        
        print(f"{Colors.BOLD}Status Breakdown:{Colors.ENDC}")
        for status, count in stats['by_status'].items():
            print(f"  {status.capitalize()}: {count}")
        
        print(f"\n{Colors.BOLD}Category Breakdown:{Colors.ENDC}")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")
        
        print(f"\n{Colors.BOLD}Performance Metrics:{Colors.ENDC}")
        print(f"  Average Completion Time: {stats['avg_completion_hours']} hours")
        print(f"  {Colors.FAIL}Overdue Tasks: {stats['overdue']}{Colors.ENDC}")
        print()

class Application:
    """Main application controller"""
    
    def __init__(self):
        self.manager = TaskManager()
        self.ui = UI()
        self.running = True
    
    def run(self):
        """Main application loop"""
        while self.running:
            self.ui.clear()
            self.ui.print_header("📋 ADVANCED TASK MANAGER")
            self.show_menu()
            
            choice = input(f"\n{Colors.CYAN}Enter choice: {Colors.ENDC}").strip()
            self.handle_choice(choice)
    
    def show_menu(self):
        """Display main menu"""
        menu_items = [
            "1. ➕ Add New Task",
            "2. 📋 View All Tasks",
            "3. ✏️  Update Task",
            "4. ✅ Complete Task",
            "5. 🗑️  Delete Task",
            "6. 📊 View Statistics",
            "7. 💾 Export Tasks",
            "8. 📥 Import Tasks",
            "9. 🔍 Search Tasks",
            "0. 🚪 Exit"
        ]
        
        for item in menu_items:
            print(f"  {item}")
    
    def handle_choice(self, choice: str):
        """Handle menu choice"""
        actions = {
            '1': self.add_task_interactive,
            '2': self.view_tasks,
            '3': self.update_task_interactive,
            '4': self.complete_task_interactive,
            '5': self.delete_task_interactive,
            '6': self.view_statistics,
            '7': self.export_tasks_interactive,
            '8': self.import_tasks_interactive,
            '9': self.search_tasks,
            '0': self.exit_app
        }
        
        action = actions.get(choice)
        if action:
            action()
        else:
            print(f"{Colors.FAIL}Invalid choice!{Colors.ENDC}")
            input("Press Enter to continue...")
    
    def add_task_interactive(self):
        """Interactive task addition"""
        self.ui.clear()
        self.ui.print_header("➕ ADD NEW TASK")
        
        title = input("Title: ").strip()
        if not title:
            print(f"{Colors.FAIL}Title cannot be empty!{Colors.ENDC}")
            input("Press Enter to continue...")
            return
        
        description = input("Description (optional): ").strip()
        category = input("Category (default: general): ").strip() or "general"
        
        estimated_hours = input("Estimated hours (0 for none): ").strip()
        estimated_hours = float(estimated_hours) if estimated_hours else 0
        
        deadline_str = input("Deadline (YYYY-MM-DD, optional): ").strip()
        deadline = None
        deadline_days = None
        
        if deadline_str:
            try:
                deadline_dt = datetime.strptime(deadline_str, '%Y-%m-%d')
                deadline = deadline_dt.isoformat()
                deadline_days = (deadline_dt - datetime.now()).days
            except ValueError:
                print(f"{Colors.WARNING}Invalid date format, skipping deadline{Colors.ENDC}")
        
        # ML-based priority suggestion
        suggested_priority = self.manager.ml_model.suggest_priority(
            category, estimated_hours, deadline_days
        )
        
        print(f"\n{Colors.GREEN}Suggested Priority: {suggested_priority}{Colors.ENDC}")
        priority = input(f"Priority 1-5 (default: {suggested_priority}): ").strip()
        priority = int(priority) if priority else suggested_priority
        
        tags_str = input("Tags (comma-separated, optional): ").strip()
        tags = [t.strip() for t in tags_str.split(',')] if tags_str else []
        
        task_id = self.manager.add_task(
            title=title,
            description=description,
            category=category,
            priority=priority,
            deadline=deadline,
            estimated_hours=estimated_hours,
            tags=tags
        )
        
        print(f"\n{Colors.GREEN}✅ Task added successfully! (ID: {task_id}){Colors.ENDC}")
        input("Press Enter to continue...")
    
    def view_tasks(self):
        """View all tasks"""
        self.ui.clear()
        self.ui.print_header("📋 ALL TASKS")
        
        status = input("Filter by status (pending/completed/all): ").strip().lower()
        status = status if status != 'all' else None
        
        tasks = self.manager.get_tasks(status=status)
        
        if not tasks:
            print(f"{Colors.WARNING}No tasks found!{Colors.ENDC}")
        else:
            for idx, task in enumerate(tasks, 1):
                self.ui.print_task(task, idx)
        
        input("Press Enter to continue...")
    
    def update_task_interactive(self):
        """Interactive task update"""
        self.ui.clear()
        self.ui.print_header("✏️  UPDATE TASK")
        
        task_id = input("Enter task ID: ").strip()
        if not task_id.isdigit():
            print(f"{Colors.FAIL}Invalid task ID!{Colors.ENDC}")
            input("Press Enter to continue...")
            return
        
        print("\nLeave blank to keep current value")
        title = input("New title: ").strip()
        priority = input("New priority (1-5): ").strip()
        status = input("New status (pending/in_progress/completed): ").strip()
        
        updates = {}
        if title:
            updates['title'] = title
        if priority:
            updates['priority'] = int(priority)
        if status:
            updates['status'] = status
        
        if updates:
            self.manager.update_task(int(task_id), **updates)
            print(f"\n{Colors.GREEN}✅ Task updated successfully!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}No changes made{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def complete_task_interactive(self):
        """Interactive task completion"""
        self.ui.clear()
        self.ui.print_header("✅ COMPLETE TASK")
        
        task_id = input("Enter task ID: ").strip()
        if not task_id.isdigit():
            print(f"{Colors.FAIL}Invalid task ID!{Colors.ENDC}")
            input("Press Enter to continue...")
            return
        
        actual_hours = input("Actual hours spent (optional): ").strip()
        actual_hours = float(actual_hours) if actual_hours else None
        
        self.manager.complete_task(int(task_id), actual_hours)
        print(f"\n{Colors.GREEN}✅ Task marked as completed!{Colors.ENDC}")
        input("Press Enter to continue...")
    
    def delete_task_interactive(self):
        """Interactive task deletion"""
        self.ui.clear()
        self.ui.print_header("🗑️  DELETE TASK")
        
        task_id = input("Enter task ID: ").strip()
        if not task_id.isdigit():
            print(f"{Colors.FAIL}Invalid task ID!{Colors.ENDC}")
            input("Press Enter to continue...")
            return
        
        confirm = input(f"{Colors.WARNING}Are you sure? (yes/no): {Colors.ENDC}").strip().lower()
        
        if confirm == 'yes':
            self.manager.delete_task(int(task_id))
            print(f"\n{Colors.GREEN}✅ Task deleted!{Colors.ENDC}")
        else:
            print(f"{Colors.CYAN}Cancelled{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def view_statistics(self):
        """View task statistics"""
        self.ui.clear()
        stats = self.manager.get_statistics()
        self.ui.print_statistics(stats)
        input("Press Enter to continue...")
    
    def export_tasks_interactive(self):
        """Interactive task export"""
        self.ui.clear()
        self.ui.print_header("💾 EXPORT TASKS")
        
        filename = input("Filename (without extension): ").strip()
        format_type = input("Format (json/csv): ").strip().lower()
        
        if format_type not in ['json', 'csv']:
            print(f"{Colors.FAIL}Invalid format!{Colors.ENDC}")
            input("Press Enter to continue...")
            return
        
        full_filename = f"{filename}.{format_type}"
        self.manager.export_tasks(full_filename, format_type)
        print(f"\n{Colors.GREEN}✅ Tasks exported to {full_filename}!{Colors.ENDC}")
        input("Press Enter to continue...")
    
    def import_tasks_interactive(self):
        """Interactive task import"""
        self.ui.clear()
        self.ui.print_header("📥 IMPORT TASKS")
        
        filename = input("Filename (with extension): ").strip()
        
        if not os.path.exists(filename):
            print(f"{Colors.FAIL}File not found!{Colors.ENDC}")
            input("Press Enter to continue...")
            return
        
        try:
            self.manager.import_tasks(filename)
            print(f"\n{Colors.GREEN}✅ Tasks imported successfully!{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Error importing: {str(e)}{Colors.ENDC}")
        
        input("Press Enter to continue...")
    
    def search_tasks(self):
        """Search tasks by keyword"""
        self.ui.clear()
        self.ui.print_header("🔍 SEARCH TASKS")
        
        keyword = input("Search keyword: ").strip().lower()
        
        all_tasks = self.manager.get_tasks()
        matching_tasks = [
            task for task in all_tasks
            if keyword in task['title'].lower() or 
               keyword in task['description'].lower() or
               keyword in task['category'].lower() or
               any(keyword in tag.lower() for tag in task['tags'])
        ]
        
        if not matching_tasks:
            print(f"{Colors.WARNING}No matching tasks found!{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}Found {len(matching_tasks)} task(s):{Colors.ENDC}\n")
            for idx, task in enumerate(matching_tasks, 1):
                self.ui.print_task(task, idx)
        
        input("Press Enter to continue...")
    
    def exit_app(self):
        """Exit application"""
        print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.ENDC}")
        self.manager.db.close()
        self.running = False

def main():
    """Application entry point"""
    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {str(e)}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()