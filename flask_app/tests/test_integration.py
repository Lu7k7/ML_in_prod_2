import unittest
import os
from app import create_app
from extensions import db
from models import User, Task

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Configuration de l'environnement de test
        # On force l'utilisation de SQLite en mémoire avant de créer l'app, ça évite de polluer la base de données de développement
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        
        self.app = create_app()
        self.app.config["TESTING"] = True
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        # Nettoyage de la variable d'environnement
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

    

    def test_register_and_login_flow(self):
        # --- Étape 1 : Inscription (Register) ---
        response = self.client.post("/register", data={
            "username": "new_integration_user",
            "password": "password123",
            "confirm": "password123"
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        
        user = User.query.filter_by(username="new_integration_user").first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("password123"))

        # --- Étape 2 : Connexion (Login) ---
        response = self.client.post("/login", data={
            "username": "new_integration_user",
            "password": "password123"
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Logged in successfully", response.data)

    def test_create_task(self):
        # --- Étape 1 : Connexion ---
        self.client.post("/register", data={
            "username": "task_creator",
            "password": "password123",
            "confirm": "password123"
        })
        self.client.post("/login", data={
            "username": "task_creator",
            "password": "password123"
        }, follow_redirects=True)

        # --- Étape 2 : Création de la tâche ---
        response = self.client.post("/tasks/new", data={
            "title": "Integration Test Task",
            "description": "Testing task creation",
            "due_date": "2025-12-31"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task created", response.data)
        
        task = Task.query.filter_by(title="Integration Test Task").first()
        self.assertIsNotNone(task)
        self.assertEqual(task.description, "Testing task creation")


    def test_edit_and_toggle_task(self):
        # --- Étape 1 : Setup: User + Login + Task Creation ---
        self.client.post("/register", data={
            "username": "task_editor",
            "password": "password123",
            "confirm": "password123"
        })
        self.client.post("/login", data={
            "username": "task_editor",
            "password": "password123"
        }, follow_redirects=True)
        
        self.client.post("/tasks/new", data={
            "title": "Original Task",
            "description": "Original Description",
            "due_date": "2025-01-01"
        }, follow_redirects=True)
        
        task = Task.query.filter_by(title="Original Task").first()
        self.assertIsNotNone(task)
        task_id = task.id

        # --- Étape 2 : Edit the task ---
        response = self.client.post(f"/tasks/{task_id}/edit", data={
            "title": "Updated Task",
            "description": "Updated Description",
            "due_date": "2025-02-02",
            "is_completed": "" # Not completed
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task updated", response.data)
        
        db.session.refresh(task)
        self.assertEqual(task.title, "Updated Task")    
        self.assertEqual(task.description, "Updated Description")
        
        # --- Étape 3 : Toggle the task ---
        response = self.client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task status updated", response.data)
        
        db.session.refresh(task)
        self.assertTrue(task.is_completed)