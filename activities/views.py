from devpulse import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta, datetime
import requests
from .models import Activity
from .serializers import ActivitySerializer

from firebase_admin import auth as firebase_auth
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Loads .env from current working directory

FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

class TestAuthView(APIView):
    """Test endpoint to verify Firebase authentication"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Authenticated",
            "firebase_uid": request.user.uid
        })

class LoginView(APIView):
    """
    Login endpoint that:
    - Creates Firebase user if not exists
    - Logs in via Firebase Auth REST API
    - Returns ID token
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------------------------
        # 1. Ensure Firebase user exists (create if missing)
        # --------------------------------------------------
        try:
            user = firebase_auth.get_user_by_email(email)
        except firebase_auth.UserNotFoundError:
            try:
                user = firebase_auth.create_user(
                    email=email,
                    password=password
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to create user: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # --------------------------------------------------
        # 2. Login via Firebase Auth REST API
        # --------------------------------------------------
        try:
            firebase_url = (
                "https://identitytoolkit.googleapis.com/v1/"
                f"accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            )

            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }

            res = requests.post(firebase_url, json=payload, timeout=10)

            if res.status_code != 200:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            data = res.json()

            return Response(
                {
                    "uid": data["localId"],
                    "email": data["email"],
                    "id_token": data["idToken"],
                    "refresh_token": data["refreshToken"],
                    "expires_in": data["expiresIn"]
                },
                status=status.HTTP_200_OK
            )

        except requests.RequestException as e:
            return Response(
                {"error": f"Firebase login failed: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class SignupView(APIView):
    """
    Create a Firebase Auth user via Django backend
    """

    authentication_classes = []  # public endpoint
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = firebase_auth.create_user(
                email=email,
                password=password
            )

            return Response(
                {
                    "message": "User created successfully",
                    "uid": user.uid,
                    "email": user.email
                },
                status=status.HTTP_201_CREATED
            )

        except firebase_auth.EmailAlreadyExistsError:
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_409_CONFLICT
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActivityView(APIView):
    """Handle activity creation and listing"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new activity"""
        data = request.data.copy()
        data['user_uid'] = request.user.uid
        
        serializer = ActivitySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """List all activities for authenticated user"""
        activities = Activity.objects.filter(user_uid=request.user.uid)
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class StreakView(APIView):
    """Calculate current and longest streak"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_uid = request.user.uid
        dates = set(
            Activity.objects.filter(user_uid=user_uid)
            .values_list('date', flat=True)
            .distinct()
        )

        if not dates:
            return Response({'current_streak': 0, 'longest_streak': 0})

        # Current streak: count backwards from latest date
        today = max(dates)
        current = today
        current_streak = 0
        while current in dates:
            current_streak += 1
            current -= timedelta(days=1)

        # Longest streak
        sorted_dates = sorted(dates)
        longest = current_run = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] == sorted_dates[i - 1] + timedelta(days=1):
                current_run += 1
            else:
                longest = max(longest, current_run)
                current_run = 1
        longest = max(longest, current_run)

        # Check if streak is broken (no activity today)
        today_date = datetime.now().date()
        if today_date not in dates and dates:
            print(f"⚠️ Streak broken for user {user_uid} - Last activity: {today}")

        return Response({
            'current_streak': current_streak,
            'longest_streak': longest
        })


class GitHubActivityView(APIView):
    """Fetch and sync activities from GitHub"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Sync GitHub activities for a user
        Expects: {"github_username": "username", "github_token": "optional_token"}
        """
        github_username = request.data.get('github_username')
        github_token = request.data.get('github_token')  # Optional for private repos

        if not github_username:
            return Response(
                {"error": "github_username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch GitHub events
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'

            response = requests.get(
                f'https://api.github.com/users/{github_username}/events',
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                return Response(
                    {"error": f"GitHub API error: {response.status_code}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            events = response.json()
            activities_created = 0

            # Map GitHub events to activities
            for event in events[:30]:  # Last 30 events
                event_type = event.get('type')
                created_at = event.get('created_at')
                
                if not created_at:
                    continue

                # Parse date
                event_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ').date()

                # Map event types to activity types
                activity_type = None
                if event_type in ['PushEvent', 'PullRequestEvent', 'CreateEvent']:
                    activity_type = 'coding'
                elif event_type in ['IssuesEvent', 'IssueCommentEvent']:
                    activity_type = 'debugging'
                elif event_type in ['WatchEvent', 'ForkEvent']:
                    activity_type = 'learning'

                if activity_type:
                    # Create or update activity
                    _, created = Activity.objects.get_or_create(
                        user_uid=request.user.uid,
                        date=event_date,
                        activity_type=activity_type
                    )
                    if created:
                        activities_created += 1

            return Response({
                "message": f"Successfully synced {activities_created} activities from GitHub",
                "github_username": github_username,
                "events_processed": len(events)
            })

        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch GitHub data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GitHubStatsView(APIView):
    """Get GitHub statistics for a user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get GitHub stats
        Query params: ?github_username=username&github_token=optional_token
        """
        github_username = request.query_params.get('github_username')
        github_token = request.query_params.get('github_token')

        if not github_username:
            return Response(
                {"error": "github_username query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'

            # Fetch user data
            user_response = requests.get(
                f'https://api.github.com/users/{github_username}',
                headers=headers,
                timeout=10
            )

            if user_response.status_code != 200:
                return Response(
                    {"error": f"GitHub API error: {user_response.status_code}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_data = user_response.json()

            # Fetch recent events
            events_response = requests.get(
                f'https://api.github.com/users/{github_username}/events',
                headers=headers,
                timeout=10
            )

            events = events_response.json() if events_response.status_code == 200 else []

            # Calculate activity stats
            push_events = sum(1 for e in events if e.get('type') == 'PushEvent')
            pr_events = sum(1 for e in events if e.get('type') == 'PullRequestEvent')
            
            # Get commit count from push events
            total_commits = 0
            for event in events:
                if event.get('type') == 'PushEvent':
                    commits = event.get('payload', {}).get('commits', [])
                    total_commits += len(commits)

            return Response({
                "github_username": github_username,
                "public_repos": user_data.get('public_repos', 0),
                "followers": user_data.get('followers', 0),
                "following": user_data.get('following', 0),
                "recent_activity": {
                    "push_events": push_events,
                    "pull_requests": pr_events,
                    "total_commits": total_commits,
                    "events_count": len(events)
                },
                "profile_url": user_data.get('html_url'),
                "bio": user_data.get('bio'),
                "created_at": user_data.get('created_at')
            })

        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch GitHub data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )