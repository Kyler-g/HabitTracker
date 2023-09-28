from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, TemplateView

from core.models import Habit, CompletedTask

from .forms import HabitForm


# Create your views here.

class HabitListView(LoginRequiredMixin, ListView):
    template_name = 'pages/habit_list_page.html'
    context_object_name = 'habit_list'
    form_class = HabitForm
    model = Habit
    success_url = reverse_lazy('habit_list_view')

    def get_queryset(self, *args, **kwargs):
        super().get_queryset()
        qs = self.model.objects.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context


class HabitCreateView(LoginRequiredMixin, CreateView):
    template_name = 'pages/habit_list_page.html'
    form_class = HabitForm
    model = Habit
    # Redirect URL after successful form submission
    success_url = reverse_lazy('habit_list_view')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MarkCompletedView(LoginRequiredMixin, View):
    def get(self, request, habit_id):
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        completed_today = habit.completedtask_set.filter(completed_date=date.today()).exists()

        if not completed_today:
            # Check if the habit was completed yesterday
            completed_yesterday = habit.completedtask_set.filter(
                completed_date=date.today() - timedelta(days=1)).exists()

            if completed_yesterday:
                habit.current_streak += 1
                # the broken streak will be false when user achieved current streak equal to 2
                habit.broken = False
                # if current streak is larger than the longest streak then swap the values.
                if habit.current_streak > habit.longest_streak:
                    habit.longest_streak = habit.current_streak
            else:
                # Habit was not completed yesterday, reset current streak, broken & missed completion field.
                habit.current_streak = 1
                habit.missed_completions = 0

            # Create a CompletedTask instance to mark the habit as completed for today
            CompletedTask.objects.create(habit=habit, completed_date=date.today())

            # Update the last completed date
            habit.last_completed_date = date.today()
            habit.save()

            # Check if the habit is broken
            if habit.frequency == 'daily':
                habit.broken = habit.missed_completions >= habit.periodicity
            elif habit.frequency == 'weekly':
                # Calculate the date range for the specified periodicity
                start_date = date.today() - timedelta(weeks=1)
                # getting count how many times user missed the completion of the habit.
                missed_completions = CompletedTask.objects.filter(
                    habit=habit,
                    completed_date__range=(start_date, date.today())
                ).count()

                # Check if the user completed the weekly habit goal
                if missed_completions >= (habit.periodicity - habit.current_streak):
                    # If missed completions are greater than or equal to the remaining completions needed
                    # then the habit is considered broken
                    habit.broken = True
                else:
                    # User still has remaining completions to achieve the goal
                    habit.broken = False

        return redirect('habit_list_view')


class AnalyticsQuestionAnswerView(TemplateView):
    template_name = 'pages/habit_analytics.html'  # Create a template for displaying the analytics

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Find the habit with the longest streak
        longest_streak_habit = Habit.objects.filter(user=self.request.user).order_by('-longest_streak').first()

        # Find the habit with the most broken streak
        most_broken_streak_habit = Habit.objects.filter(user=self.request.user).order_by('-missed_completions').first()

        context['longest_streak_habit'] = longest_streak_habit
        context['most_broken_streak_habit'] = most_broken_streak_habit

        return context
