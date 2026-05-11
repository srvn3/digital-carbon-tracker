# Google OAuth 2.0 Setup Guide for CarbonTracker

## Overview
This guide walks you through setting up Google Sign-In OAuth 2.0 authentication for your CarbonTracker Flask application.

## Prerequisites
- Google account
- Access to Google Cloud Console
- Your Flask application running (or ready to run)

---

## Step 1: Install Required Dependencies

First, ensure all OAuth dependencies are installed:

```bash
pip install -r requirements.txt
```

This installs:
- `google-auth-oauthlib==1.2.0`
- `google-auth-httplib2==0.2.0`
- `google-auth==2.26.1`
- `requests==2.31.0`
- `python-dotenv==1.0.0`

---

## Step 2: Set Up Google Cloud Project

### 2.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project selector dropdown at the top
3. Click **"NEW PROJECT"**
4. Enter project name (e.g., "CarbonTracker OAuth")
5. Click **"CREATE"**

### 2.2 Enable Google+ API
1. In the Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"**
3. Click on it and select **"ENABLE"**

### 2.3 Create OAuth 2.0 Credentials
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. You may be prompted to configure the OAuth consent screen first:
   - Click **"Configure Consent Screen"**
   - Select **"External"** as the user type
   - Fill in required fields:
     - **App name**: CarbonTracker
     - **User support email**: your-email@example.com
     - **Developer contact**: your-email@example.com
   - Add scopes:
     - `openid`
     - `email`
     - `profile`
   - Save and continue

4. After consent screen is configured, go back to **"Credentials"**
5. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
6. Select **"Web application"** as the application type
7. Name it (e.g., "CarbonTracker Web Client")
8. Add **Authorized JavaScript origins**:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   ```
   (Add your production domain later if applicable)

9. Add **Authorized redirect URIs**:
   ```
   http://localhost:5000/auth/callback
   http://127.0.0.1:5000/auth/callback
   ```
   (Add your production URL later if applicable)

10. Click **"CREATE"**
11. Copy your **Client ID** and **Client Secret**

---

## Step 3: Configure Environment Variables

### 3.1 Create .env File
Create a `.env` file in your project root (same level as `app.py`):

```bash
cp .env.example .env
```

### 3.2 Fill in the .env File
Edit `.env` and add your credentials:

```env
# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

# Flask secret key (generate a secure random key)
FLASK_SECRET_KEY=your-random-secret-key-here
```

**⚠️ IMPORTANT:**
- **NEVER** commit the `.env` file to version control
- The `.env` file contains sensitive credentials

---

## Step 4: Update Database Schema

If you have an existing `digital_carbon_tracker` database, add the `google_id` column to the `users` table:

```sql
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE DEFAULT NULL;
```

If you're creating a fresh database, the schema is already configured in `schema.sql`.

---

## Step 5: Test the Integration

### 5.1 Run the Flask Application
```bash
python app.py
```

The application should start on `http://localhost:5000`

### 5.2 Test Login Flow
1. Navigate to http://localhost:5000/login
2. Click **"Continue with Google"**
3. You'll be redirected to Google's account chooser
4. Select your Google account
5. Grant permissions if prompted
6. You should be redirected to the dashboard with your Gmail displayed

---

## Step 6: Production Deployment

### 6.1 Update Redirect URIs in Google Cloud Console
When deploying to production:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **"APIs & Services"** → **"Credentials"**
3. Click on your OAuth client ID
4. Update **Authorized JavaScript origins**:
   ```
   https://yourdomain.com
   https://www.yourdomain.com
   ```

5. Update **Authorized redirect URIs**:
   ```
   https://yourdomain.com/auth/callback
   https://www.yourdomain.com/auth/callback
   ```

### 6.2 Update .env for Production
```env
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback
FLASK_SECRET_KEY=generate-a-long-random-production-key
```

### 6.3 Use a Secure Secret Key
Generate a production-grade secret key:
```python
import secrets
print(secrets.token_hex(32))
```

---

## Features Implemented

### ✅ Google Sign-In
- Modern, animated login UI
- Google account chooser popup (with `prompt=select_account`)
- Secure OAuth 2.0 flow

### ✅ User Management
- Auto-create user accounts from Google profile
- Link existing email accounts with Google ID
- Store Gmail in session for display

### ✅ Session Management
- Secure session handling
- Store Google email and auth method
- Display Google email on dashboard

### ✅ Error Handling
- Check for missing credentials
- Network error handling
- User-friendly error messages

### ✅ Security Features
- Use environment variables for secrets
- HTTPS-ready for production
- Token validation
- Secure callback handling

---

## How It Works

### Authentication Flow
```
1. User clicks "Continue with Google"
   ↓
2. Redirected to /auth/google
   ↓
3. Redirected to Google OAuth URL with prompt=select_account
   ↓
4. User selects Google account and grants permissions
   ↓
5. Google redirects back to /auth/callback with authorization code
   ↓
6. Flask exchanges code for access token
   ↓
7. Flask retrieves user information from Google
   ↓
8. User is created or updated in database
   ↓
9. Session is created and user is redirected to dashboard
   ↓
10. Dashboard displays user info with Google email badge
```

### Files Modified
- `app.py`: Added OAuth routes and Google configuration
- `schema.sql`: Added `google_id` column to users table
- `requirements.txt`: Added OAuth libraries
- `.env.example`: Configuration template
- `templates/login.html`: Google Sign-In button with proper UI
- `templates/register.html`: Google Sign-In button for registration
- `templates/dashboard.html`: Google email badge display
- `static/css/main.css`: Enhanced styling for Google button and header

---

## Session Data

When a user logs in with Google, the following is stored in the session:
```python
{
    'loggedin': True,
    'user_id': 123,                      # Database user ID
    'username': 'John Doe',              # Name from Google profile
    'email': 'john@example.com',         # Email from database
    'google_email': 'john@gmail.com',    # Google account email
    'auth_method': 'google'              # Authentication method
}
```

---

## Troubleshooting

### Issue: "Google Sign-In is not configured"
**Solution**: 
- Ensure `.env` file exists and is in the project root
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Verify they're not empty strings

### Issue: Redirect URI mismatch error
**Solution**:
- Check that redirect URI in `.env` matches Google Cloud Console exactly
- For localhost, use `http://localhost:5000/auth/callback`
- For production, use `https://yourdomain.com/auth/callback`

### Issue: User not being created
**Solution**:
- Ensure database migration has been run
- Check that the users table has the `google_id` column
- Verify MySQL connection is working

### Issue: Session data not persisting
**Solution**:
- Ensure `FLASK_SECRET_KEY` is set in `.env`
- Check that cookies are enabled in browser
- Verify Flask is running in appropriate environment

---

## Security Best Practices

1. **Always use HTTPS** in production
2. **Never commit .env** file to version control
3. **Rotate secrets** regularly in production
4. **Use strong secret keys** (minimum 32 characters)
5. **Keep dependencies updated** regularly
6. **Validate all user inputs** before using them
7. **Use environment variables** for all sensitive data
8. **Enable CSRF protection** for forms

---

## Next Steps

1. Test the complete authentication flow
2. Customize user profile page
3. Add email verification (optional)
4. Set up password reset for email accounts
5. Implement social login with other providers (GitHub, Facebook, etc.)

---

## Support

For issues with:
- **Google OAuth**: Visit [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- **Flask Integration**: Check [Flask Documentation](https://flask.palletsprojects.com/)
- **Database**: Review [MySQL Documentation](https://dev.mysql.com/doc/)

---

**Last Updated**: May 2026
