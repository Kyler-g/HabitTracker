import datetime
# Create your tests here.
from django.test import TestCase
from django.urls import reverse

from core.forms import HabitForm
from core.models import Habit, CompletedTask
from django.contrib.auth.models import User


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.habit = Habit.objects.create(user=self.user, task='Test Habit', periodicity=3, frequency='weekly')

        self.habit1 = Habit.objects.create(user=self.user, task='Habit 1', periodicity=3, frequency='daily')
        self.habit2 = Habit.objects.create(user=self.user, task='Habit 2', periodicity=2, frequency='daily')
        self.habit3 = Habit.objects.create(user=self.user, task='Habit 3', periodicity=1, frequency='weekly')

    def test_habit_creation(self):
        self.assertEqual(str(self.habit), self.habit.task)

    def test_habit_list_view_for_verified_user(self):
        logged_in = self.client.login(username='testuser', password='password123')

        # Check if login was successful
        self.assertTrue(logged_in)

        response = self.client.get(reverse('habit_list_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Habit')

    def test_habit_form_valid(self):
        form_data = {'task': 'Test Habit', 'periodicity': 3, 'frequency': 'weekly'}
        form = HabitForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_habit_form_invalid(self):
        form_data = {'task': '', 'periodicity': -1, 'frequency': 'invalid_frequency'}
        form = HabitForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_streak_broken_for_daily_habit(self):
        # Log in the user
        self.client.login(username='testuser', password='password123')
        # simulation for two days consecutive streak.
        today = datetime.date.today()
        for day_offset in range(1, 3):
            completed_date = today - datetime.timedelta(days=day_offset)
            self.habit.current_streak += 1
            self.habit.longest_streak += 1
            self.habit.save()
            CompletedTask.objects.create(habit=self.habit, completed_date=completed_date)

        # Visit the habit list view
        response = self.client.get(reverse('habit_list_view'))

        # check the current streak status
        self.assertEqual(self.habit.current_streak, 2)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Habit')
        self.assertContains(response, "Current Streak: 2")

        # simulation for broken streak.
        self.habit.completedtask_set.all().delete()
        for day_offset in range(1, 4):
            completed_date = today - datetime.timedelta(days=day_offset)
            if day_offset != 3:  # Simulate habit not completed on the second day
                CompletedTask.objects.create(habit=self.habit, completed_date=completed_date)

            else:
                self.habit.broken = True
                self.habit.save()
                # go to habit list view
                response = self.client.get(reverse('habit_list_view'))
                self.assertEqual(self.habit.broken, True)
                # check the status of streak is broken in the template
                self.assertContains(response, 'Your Streak is Broken.')

    def test_longest_streak(self):
        # Simulate completing habit1 for a streak of 5 days
        for day_offset in range(1, 6):
            completed_date = datetime.date.today() - datetime.timedelta(days=day_offset)
            self.habit.longest_streak += 1
            CompletedTask.objects.create(habit=self.habit, completed_date=completed_date)
        self.habit.save()
        # Check the longest streak for habit1
        self.assertEqual(self.habit.longest_streak, 5)


class CompletedTaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.habit = Habit.objects.create(user=self.user, task='Test Habit', periodicity=3, frequency='weekly')
        self.completed_task = CompletedTask.objects.create(habit=self.habit, completed_date=datetime.date.today())

    def test_completed_task_creation(self):
        self.assertEqual(self.completed_task.habit, self.habit)
