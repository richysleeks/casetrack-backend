from django.urls import path
# from .views import TaskListCreateView, TaskDetailView

# urlpatterns = [
#     path('', TaskListCreateView.as_view(), name='task-list'),
#     path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
# ]


from . import views
urlpatterns = [
    path('', views.tasks_list, name='tasks-list'),
    path('stats/', views.tasks_stats, name='tasks-stats'),
    path('<int:pk>/', views.task_detail, name='task-detail'),
]