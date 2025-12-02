import unittest
from datetime import date, timedelta
from models import User, Task



class TestModels(unittest.TestCase):
    def test_user_password_hashing(self):
        user = User(username="testuser")
        user.set_password("testpassword")

        self.assertTrue(user.check_password("testpassword"))
        self.assertFalse(user.check_password("wrongpassword"))
        self.assertNotEqual(user.password_hash, "testpassword")
    def test_task_overdue(self):
        today = date.today()

        future_task = Task(due_date=today + timedelta(days=1))
        self.assertFalse(future_task.is_overdue())

        past_task = Task(due_date=today - timedelta(days=1))
        self.assertTrue(past_task.is_overdue())

        completed_task = Task(
            due_date=today - timedelta(days=1), is_completed=True
        )
        self.assertFalse(completed_task.is_overdue())



if __name__ == '__main__':
    unittest.main()