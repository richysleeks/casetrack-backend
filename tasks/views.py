# from rest_framework import generics

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Task
from .serializers import TaskSerializer

# class TaskListCreateView(generics.ListCreateAPIView):
#     queryset = Task.objects.all().order_by("created_at")
#     serializer_class = TaskSerializer

# class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer



@api_view(["GET"])
def tasks_stats(request):
    now = timezone.now()
    overdue_count = Task.objects.filter(due_date__lt=now).exclude(status="done").count()
    return Response(
        {
            "message": "Stats retrieved successfully",
            "data": {
                "todo": Task.objects.filter(status="todo").count(),
                "in_progress": Task.objects.filter(status="in_progress").count(),
                "done": Task.objects.filter(status="done").count(),
                "total": Task.objects.count(),
                "overdue": overdue_count,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
def tasks_list(request):
    if request.method == "GET":
        status_param = request.query_params.get("status")
        tasks = Task.objects.all().order_by("created_at")

        if status_param == "overdue":
            tasks = tasks.filter(due_date__lt=timezone.now()).exclude(status="done")
        elif status_param in ("todo", "in_progress", "done"):
            tasks = tasks.filter(status=status_param)

        serializer = TaskSerializer(tasks, many=True)
        return Response(
            {
                "message": "Tasks retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    if request.method == "POST":
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Task created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "message": "Validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

@api_view(["GET", "PATCH", "DELETE"])
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "GET":
        serializer = TaskSerializer(task)
        return Response(
            {
                "message": "Task retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    if request.method == "PATCH":
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Task updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": "Validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if request.method == "DELETE":
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

