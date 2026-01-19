from django.db import models
from django.utils import timezone

class Activity(models.Model):
    """Track daily developer activities"""
    
    ACTIVITY_TYPES = [
        ('coding', 'Coding'),
        ('learning', 'Learning'),
        ('debugging', 'Debugging'),
    ]

    user_uid = models.CharField(max_length=128, db_index=True)  # Firebase UID
    date = models.DateField(db_index=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    created_at = models.DateTimeField(default=timezone.now())

    class Meta:
        unique_together = ('user_uid', 'date', 'activity_type')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user_uid', '-date']),
        ]

    def __str__(self):
        return f"{self.user_uid} - {self.activity_type} on {self.date}"


class GitHubProfile(models.Model):
    """Store GitHub profile information for users"""
    
    user_uid = models.CharField(max_length=128, unique=True, db_index=True)
    github_username = models.CharField(max_length=255)
    github_token = models.CharField(max_length=255, blank=True, null=True)  # Encrypted in production
    last_synced = models.DateTimeField(null=True, blank=True)
    auto_sync = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now())
    updated_at = models.DateTimeField(default=timezone.now())

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.github_username} ({self.user_uid})"