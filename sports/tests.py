from django.test import TestCase
from django.contrib.auth import get_user_model
from sports.models import Project, ProjectMembership, ProjectFile, ProjectMessage

User = get_user_model()

class CommonUserTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='testpass', email='testuser@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertFalse(user.is_admin)

class ProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(title='Test Project', description='A simple test project', owner=self.user)

    def test_create_project(self):
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.owner, self.user)

    def test_add_members(self):
        new_member = User.objects.create_user(username='memberuser', password='testpass')
        ProjectMembership.objects.create(user=new_member, project=self.project, status='member')
        self.assertIn(new_member, self.project.members.all())
