# Google Sign-In OAuth 2.0 Implementation Guide

## 📋 Complete Implementation Overview

This guide covers the complete implementation of Google OAuth 2.0 Sign-In for the CarbonTracker Flask application. All changes have been made to support secure, modern authentication with Google accounts.

---

## ✨ Features Implemented

### ✅ Google Sign-In Button
- Modern, animated UI with Google logo SVG
- Available on both login and registration pages
- Professional styling matching the application design
- Clickable button that initiates OAuth flow

### ✅ OAuth 2.0 Flow
- **Account Chooser**: User is always prompted to select which Google account to use
- **Secure Token Exchange**: Authorization code exchanged for access token server-side
- **User Info Retrieval**: Google email, name, and ID securely retrieved
- **Error Handling**: Comprehensive error messages and logging

### ✅ User Management
- Auto-create new user accounts from Google profile
- Link existing email accounts with Google ID
- Support for both email and Google authentication
- Store Google email in session for display

### ✅ Dashboard Integration
- Google account email displayed as badge on dashboard
- Shows auth method alongside user information
- Optional: Disconnect Google account feature

### ✅ Security Features
- Environment variables for all sensitive credentials
- Secure session management with custom secret key
- Server-side token validation
- HTTPS-ready for production deployment
- No sensitive data in frontend code

---

## 📁 Files Modified and Created

### New Files Created
1. **`.env.example`** - Configuration template for OAuth credentials
2. **`GOOGLE_OAUTH_SETUP.md`** - Comprehensive setup guide
3. **`setup_oauth.py`** - Helper script to verify OAuth configuration
4. **`setup_oauth.py`** - Automated setup verification script

### Modified Files

#### `requirements.txt`
Added OAuth and environment dependencies:
```
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-auth==2.26.1
requests==2.31.0
python-dotenv==1.0.0
```

#### `app.py`
**Imports Added:**
```python
from dotenv import load_dotenv
import os
import json
import requests
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
```

**Configuration Added:**
```python
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/callback')

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'
```

**New Routes Added:**
- `/auth/google` - Initiates OAuth flow with account chooser
- `/auth/callback` - Handles OAuth callback from Google
- `/auth/google-disconnect` - Optional feature to disconnect Google account

**Route Features:**
```python
@app.route('/auth/google')
def auth_google():
    # Redirects to Google with prompt=select_account
    # Always shows account chooser to user
```

```python
@app.route('/auth/callback')
def auth_callback():
    # Handles Google redirect with authorization code
    # Exchanges code for access token
    # Retrieves user information
    # Creates or updates user in database
    # Establishes secure session
```

#### `schema.sql`
**Column Added to `users` table:**
```sql
google_id VARCHAR(255) UNIQUE DEFAULT NULL
```

This allows linking Google accounts to user profiles while maintaining unique Google IDs.

#### `templates/login.html`
**Changes:**
- Added Google SDK script: `<script src="https://accounts.google.com/gsi/client" async defer></script>`
- Added modern Google Sign-In button with SVG logo
- Professional "Continue with Google" button styling
- Proper button placement above email/password form

#### `templates/register.html`
**Changes:**
- Same Google OAuth button as login
- Allows new users to sign up with Google
- Seamless account creation from Google profile

#### `templates/dashboard.html`
**Changes:**
- Added Google email badge in header
- Displays Gmail when user logged in with Google
- Shows authentication method visually

#### `static/css/main.css`
**Styles Added:**
```css
.google-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background: #ffffff;
    color: #111827;
    border-color: rgba(0, 0, 0, 0.12);
    font-weight: 600;
    transition: all 0.3s ease;
}

.google-btn:hover {
    background: #f8f8f8;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.header-right {
    display: flex;
    gap: 16px;
    align-items: center;
}

.google-badge {
    background: rgba(79, 134, 255, 0.12) !important;
    border: 1px solid rgba(79, 134, 255, 0.25) !important;
}
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
```bash
cp .env.example .env
```

### 3. Get Google OAuth Credentials
Follow the detailed steps in `GOOGLE_OAUTH_SETUP.md`:
- Create Google Cloud Project
- Enable Google+ API
- Create OAuth 2.0 credentials
- Add authorized redirect URIs

### 4. Configure .env File
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback
FLASK_SECRET_KEY=generate-random-key-here
```

### 5. Update Database
If using existing database, add column:
```sql
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE DEFAULT NULL;
```

### 6. Run Setup Verification
```bash
python setup_oauth.py
```

### 7. Start Application
```bash
python app.py
```

### 8. Test Google Sign-In
1. Visit http://localhost:5000/login
2. Click "Continue with Google"
3. Select or add your Google account
4. Verify redirect to dashboard with email displayed

---

## 🔐 Security Implementation

### Secret Management
- ✅ All credentials stored in `.env` (not in code)
- ✅ `.env` should be in `.gitignore`
- ✅ Different credentials for dev and production
- ✅ Environment variables loaded at runtime

### OAuth Flow Security
- ✅ Authorization code exchange happens server-side
- ✅ No tokens exposed to browser
- ✅ Secure HTTPS required for production
- ✅ Token validation implemented
- ✅ User input validation before database operations

### Session Security
- ✅ Custom secure secret key
- ✅ Flask session with secure cookies
- ✅ User data validated before storage
- ✅ Session data cleared on logout

### Database Security
- ✅ Google ID stored separately from password
- ✅ Email treated as unique identifier
- ✅ Password field optional for OAuth users
- ✅ Data isolation per user

---

## 🔄 Authentication Flow Diagram

```
┌─────────────────────────────────────────────────┐
│  User clicks "Continue with Google"             │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ /auth/google route   │
          │ Redirects to Google  │
          └─────────┬────────────┘
                    │
                    ▼
          ┌──────────────────────────────────┐
          │ Google OAuth 2.0 Authorization   │
          │ with prompt=select_account       │
          │ (Always shows account chooser)   │
          └─────────┬────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────┐
    │ User selects Google account               │
    │ Grants permission to access email/profile │
    └────────────┬────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Google redirects to /auth/callback     │
    │ with authorization code                │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Flask exchanges code for access token  │
    │ (Server-side, secure)                  │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Flask retrieves user info from Google  │
    │ (Google email, name, ID)               │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Check if user exists in database       │
    │ - If exists: Update with Google ID     │
    │ - If new: Create new user account      │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Create secure Flask session            │
    │ Store: user_id, email, google_email    │
    └────────────┬─────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ Redirect to dashboard                  │
    │ Display Google email badge             │
    └────────────────────────────────────────┘
```

---

## 📊 Session Data Structure

When user logs in with Google, session contains:
```python
{
    'loggedin': True,
    'user_id': 123,                    # Database user ID
    'username': 'John Doe',            # From Google profile
    'email': 'john@example.com',       # From database
    'google_email': 'john@gmail.com',  # Google account email
    'auth_method': 'google'            # Indicates OAuth login
}
```

---

## ⚙️ Configuration Details

### Environment Variables (.env)
```env
# Required: From Google Cloud Console
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx

# Required: Must match Google Cloud Console settings
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

# Required: Generate with secrets.token_hex(32)
FLASK_SECRET_KEY=xxxxx
```

### Google OAuth URLs
```
Authorization URL:
  https://accounts.google.com/o/oauth2/v2/auth
  
Token URL:
  https://oauth2.googleapis.com/token
  
User Info URL:
  https://www.googleapis.com/oauth2/v2/userinfo
```

### Scopes Requested
```
openid    - OpenID Connect
email     - Access email address
profile   - Access profile information
```

---

## 🎯 Key Implementation Points

### ✅ Account Chooser Always Shows
The `prompt=select_account` parameter ensures users always see the account selection screen:
```python
auth_uri = f"{GOOGLE_AUTH_URL}?...&prompt=select_account"
```

### ✅ Server-Side Token Exchange
Authorization code is exchanged on the server (secure):
```python
token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
# Tokens never exposed to client
```

### ✅ User Auto-Creation
New users are automatically created from Google profile:
```python
cursor.execute(
    'INSERT INTO users (username, email, google_id, ...) VALUES (...)',
    (name, email, google_id, ...)
)
```

### ✅ Email-Based Linking
Existing email accounts can be linked with Google:
```python
cursor.execute(
    'UPDATE users SET google_id = %s WHERE email = %s',
    (google_id, email)
)
```

---

## 🧪 Testing Checklist

- [ ] `python setup_oauth.py` shows all checks passing
- [ ] Login page displays Google button
- [ ] Clicking Google button redirects to Google
- [ ] Account chooser popup appears
- [ ] Selecting account redirects back to app
- [ ] Dashboard shows Gmail in badge
- [ ] User session persists across page refreshes
- [ ] Logout clears session properly
- [ ] New user creation works with Google
- [ ] Existing email user can link Google account
- [ ] Error messages display properly for OAuth failures

---

## 📱 Production Deployment

### Environment Setup
```bash
# Generate secure key
python -c "import secrets; print(secrets.token_hex(32))"

# Create .env for production
GOOGLE_CLIENT_ID=prod-client-id
GOOGLE_CLIENT_SECRET=prod-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback
FLASK_SECRET_KEY=generated-secure-key
```

### Google Cloud Console Updates
1. Add production domain to Authorized JavaScript origins
2. Add production callback URL to Authorized redirect URIs
3. Test with production domain

### Server Configuration
- Use HTTPS only
- Set secure cookie flags
- Enable CSRF protection
- Configure firewall rules
- Use strong database credentials

---

## 🐛 Troubleshooting

### "Google Sign-In is not configured"
- Check `.env` file exists in project root
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Run `python setup_oauth.py` for diagnostics

### Redirect URI Mismatch Error
- Exact match required between `.env` and Google Console
- For localhost: `http://localhost:5000/auth/callback`
- For production: Use `https://` with correct domain

### Session Data Not Persisting
- Verify `FLASK_SECRET_KEY` is set in `.env`
- Check browser cookies are enabled
- Clear browser cookies and try again

### Database Connection Issues
- Verify MySQL is running on correct port (3307)
- Check database credentials in `app.py`
- Run `python setup_oauth.py` to verify connection

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Sign-In Guide](https://developers.google.com/identity/gsi/web)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Requests Library](https://requests.readthedocs.io/)

---

## ✅ Verification Commands

```bash
# Check dependencies
pip show google-auth-oauthlib requests python-dotenv

# Verify .env file
cat .env

# Test database connection
python -c "from app import mysql; print('Database OK')"

# Run full verification
python setup_oauth.py

# Start application
python app.py
```

---

## 📞 Support

For issues or questions:
1. Check `GOOGLE_OAUTH_SETUP.md` for detailed setup steps
2. Run `python setup_oauth.py` for diagnostics
3. Review error messages in Flask console
4. Check Google Cloud Console project settings

---

**Implementation Date**: May 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready
