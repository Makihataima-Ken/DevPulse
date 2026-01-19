param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$Email = "test@devpulse.com",
    [string]$Password = "password123"
)

function Write-Section($Title) {
    Write-Host ""
    Write-Host $Title -ForegroundColor Cyan
    Write-Host ("-" * $Title.Length) -ForegroundColor DarkGray
}

Write-Host "DevPulse Full API Test Started" -ForegroundColor Green

# ============================
# 1. LOGIN
# ============================
Write-Section "[1/7] Login"

try {
    $loginBody = @{
        email    = $Email
        password = $Password
    } | ConvertTo-Json

    $loginRes = Invoke-RestMethod `
        -Method Post `
        -Uri "$BaseUrl/api/auth/login/" `
        -ContentType "application/json" `
        -Body $loginBody

    $IdToken = $loginRes.id_token

    Write-Host "Login OK" -ForegroundColor Green
    Write-Host "UID: $($loginRes.uid)"
}
catch {
    Write-Host "Login Failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $IdToken"
    "Content-Type"  = "application/json"
}

# ============================
# 2. TEST AUTH
# ============================
Write-Section "[2/7] Test Auth"

try {
    $res = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/test-auth/" `
        -Headers $headers

    Write-Host "Auth OK - UID: $($res.firebase_uid)" -ForegroundColor Green
}
catch {
    Write-Host "Auth Test Failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# ============================
# 3. CREATE ACTIVITY
# ============================
Write-Section "[3/7] Create Activity"

try {
    $activityBody = @{
        date          = (Get-Date).ToString("yyyy-MM-dd")
        activity_type = "coding"
    } | ConvertTo-Json

    $res = Invoke-RestMethod `
        -Method Post `
        -Uri "$BaseUrl/api/activities/" `
        -Headers $headers `
        -Body $activityBody

    Write-Host "Activity Created" -ForegroundColor Green
}
catch {
    Write-Host "Create Activity Failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# ============================
# 4. LIST ACTIVITIES
# ============================
Write-Section "[4/7] List Activities"

try {
    $res = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/api/activities/" `
        -Headers $headers

    $count = if ($res) { $res.Count } else { 0 }
    Write-Host "Activities Count: $count" -ForegroundColor Green
}
catch {
    Write-Host "List Activities Failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# ============================
# 5. STREAK
# ============================
Write-Section "[5/7] Get Streak"

try {
    $res = Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/api/streak/" `
        -Headers $headers

    Write-Host "Current Streak: $($res.current_streak)"
    Write-Host "Longest Streak: $($res.longest_streak)"
}
catch {
    Write-Host "Streak Failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# ============================
# 6. GITHUB SYNC
# ============================
Write-Section "[6/7] GitHub Sync"

try {
    $githubBody = @{
        github_username = "Makihataima-Ken"
    } | ConvertTo-Json

    Invoke-RestMethod `
        -Method Post `
        -Uri "$BaseUrl/api/github/sync/" `
        -Headers $headers `
        -Body $githubBody

    Write-Host "GitHub Sync OK" -ForegroundColor Green
}
catch {
    Write-Host "GitHub Sync Failed (non-critical)" -ForegroundColor Yellow
}

# ============================
# 7. GITHUB STATS
# ============================
Write-Section "[7/7] GitHub Stats"

try {
    Invoke-RestMethod `
        -Method Get `
        -Uri "$BaseUrl/api/github/stats/?github_username=Makihataima-Ken" `
        -Headers $headers

    Write-Host "GitHub Stats OK" -ForegroundColor Green
}
catch {
    Write-Host "GitHub Stats Failed (non-critical)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "ALL TESTS COMPLETED" -ForegroundColor Green
