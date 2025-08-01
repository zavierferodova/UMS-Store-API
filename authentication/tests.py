from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    # Test case for creating a regular user
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            name='Test User',
            role='cashier',
            gender='male',
            email='test@example.com',
            phone='1234567890',
            address='123 Test St'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpassword'))
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.role, 'cashier')
        self.assertEqual(user.gender, 'male')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.phone, '1234567890')
        self.assertEqual(user.address, '123 Test St')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    # Test case for creating a superuser
    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username='adminuser',
            password='adminpassword',
            name='Admin User',
            gender='female',
            email='admin@example.com',
            phone='0987654321',
            address='456 Admin Ave'
        )
        self.assertEqual(admin_user.username, 'adminuser')
        self.assertTrue(admin_user.check_password('adminpassword'))
        self.assertEqual(admin_user.name, 'Admin User')
        self.assertEqual(admin_user.role, 'admin')
        self.assertEqual(admin_user.gender, 'female')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.phone, '0987654321')
        self.assertEqual(admin_user.address, '456 Admin Ave')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)