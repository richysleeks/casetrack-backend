from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Task


class TaskTests(APITestCase):

    def test_create_task(self):
        response = self.client.post("/tasks/", {
            "title": "Example task",
            "status": "todo"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["title"], "Example task")

    def test_get_all_tasks(self):
        Task.objects.create(title="T1", status="todo")
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["data"]) >= 1)

    def test_filter_by_status(self):
        Task.objects.create(title="Todo task", status="todo")
        Task.objects.create(title="Done task", status="done")
        response = self.client.get("/tasks/?status=todo")
        self.assertEqual(response.status_code, 200)
        results = response.data["data"]
        self.assertTrue(all(t["status"] == "todo" for t in results))

    def test_filter_overdue(self):
        past = timezone.now() - timedelta(days=1)
        future = timezone.now() + timedelta(days=1)
        Task.objects.create(title="Overdue", status="todo", due_date=past)
        Task.objects.create(title="Not due yet", status="todo", due_date=future)
        Task.objects.create(title="Done but past due", status="done", due_date=past)
        response = self.client.get("/tasks/?status=overdue")
        self.assertEqual(response.status_code, 200)
        results = response.data["data"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Overdue")

    def test_stats(self):
        past = timezone.now() - timedelta(days=1)
        Task.objects.create(title="T1", status="todo")
        Task.objects.create(title="T2", status="in_progress")
        Task.objects.create(title="T3", status="done")
        Task.objects.create(title="T4", status="todo", due_date=past)
        response = self.client.get("/tasks/stats/")
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(data["todo"], 2)
        self.assertEqual(data["in_progress"], 1)
        self.assertEqual(data["done"], 1)
        self.assertEqual(data["total"], 4)
        self.assertEqual(data["overdue"], 1)

    def test_update_status(self):
        task = Task.objects.create(title="AAA", status="todo")
        response = self.client.patch(f"/tasks/{task.id}/", {
            "status": "in_progress"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["status"], "in_progress")

    def test_delete_task(self):
        task = Task.objects.create(title="To delete", status="todo")
        response = self.client.delete(f"/tasks/{task.id}/")
        self.assertEqual(response.status_code, 204)

