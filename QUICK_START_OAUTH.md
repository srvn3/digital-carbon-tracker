# 🚀 Quick Start: Google OAuth Setup (5 Minutes)

## Step-by-Step Setup

### 1️⃣ Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### 2️⃣ Create .env File (30 sec)
```bash
cp .env.example .env
```

### 3️⃣ Get Google Credentials (3-4 min)

**Go to:** [https://console.cloud.google.com/](https://console.cloud.google.com/)

**Quick Steps:**
1. Click **"Select a Project"** → **"NEW PROJECT"**
2. Name: "CarbonTracker OAuth" → **"CREATE"**
3. Go to **"APIs & Services"** → **"Library"**
4. Search "Google+" → Click result → **"ENABLE"**
5. Go to **"Credentials"** → **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
   - If prompted: Configure consent screen first
   - App name: CarbonTracker
   - Add scopes: openid, email, profile
   - Save and continue
6. Select **"Web application"**
7. Add origins:
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   ```
8. Add redirect URIs:
   ```
   http://localhost:5000/auth/callback
   http://127.0.0.1:5000/auth/callback
   ```
9. **"CREATE"** and copy credentials

### 4️⃣ Configure .env (30 sec)

Edit `.env`:
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback
FLASK_SECRET_KEY=put-random-string-here
```

### 5️⃣ Update Database (optional, if existing DB)
```sql
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE DEFAULT NULL;
```

### 6️⃣ Run Verification
```bash
python setup_oauth.py
```

### 7️⃣ Start & Test
```bash
python app.py
```

Visit: `http://localhost:5000/login`

✅ Click **"Continue with Google"** → Select account → Done!

---

## 🎯 What You Get

✅ Google login button on login/register  
✅ Account chooser popup always shows  
✅ Auto user creation from Google  
✅ Gmail displayed on dashboard  
✅ Secure OAuth 2.0 flow  
✅ Proper error handling  

---

## 📝 Key Files

| File | Purpose |
|------|---------|
| `.env` | Store Google credentials |
| `GOOGLE_OAUTH_SETUP.md` | Detailed setup guide |
| `GOOGLE_OAUTH_README.md` | Complete documentation |
| `setup_oauth.py` | Verify configuration |

---

## 🆘 Common Issues

**"Google Sign-In not configured"**
→ Check `.env` file exists with credentials filled in

**"Redirect URI mismatch"**
→ Make sure exact match: `http://localhost:5000/auth/callback`

**"Module not found"**
→ Run: `pip install -r requirements.txt`

**"Database error"**
→ Ensure MySQL on port 3307, or add google_id column

---

## ✨ For Production

1. Update `.env` with production credentials
2. Update Google Console with production domain
3. Use HTTPS only
4. Generate strong secret key: `python -c "import secrets; print(secrets.token_hex(32))"`
5. See `GOOGLE_OAUTH_SETUP.md` for full details

---

**Ready?** Run: `python setup_oauth.py` then `python app.py`! 🎉
