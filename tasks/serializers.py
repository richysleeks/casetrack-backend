from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    due_date = serializers.DateTimeField(input_formats=["iso-8601", "%Y-%m-%dT%H:%M"], required=False, allow_null=True)
    class Meta:
        model = Task
        fields = "__all__"

