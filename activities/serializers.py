from rest_framework import serializers
from .models import Activity, GitHubProfile


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'user_uid', 'date', 'activity_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class GitHubProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubProfile
        fields = [
            'id', 'user_uid', 'github_username', 
            'last_synced', 'auto_sync', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_uid', 'last_synced', 'created_at', 'updated_at']