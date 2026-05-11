#!/usr/bin/env python3
"""
CarbonTracker Google OAuth 2.0 Setup Helper
This script helps verify and set up the Google OAuth configuration
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Creating from .env.example...")
        if Path('.env.example').exists():
            os.system('cp .env.example .env')
            print("✅ .env file created. Please edit it with your Google OAuth credentials.")
        else:
            print("❌ .env.example not found either!")
            return False
        return False
    
    print("✅ .env file found")
    
    # Check required variables
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REDIRECT_URI']
    with open('.env', 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=your-" in env_content or f"{var}=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or placeholder values: {', '.join(missing_vars)}")
        print("   Please edit .env and add your Google OAuth credentials")
        return False
    
    print("✅ All required OAuth variables are configured")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'dotenv',
        'google',
        'requests',
        'flask',
        'flask_mysqldb'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nRun this to install all dependencies:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_database():
    """Check if database has google_id column"""
    try:
        from flask import Flask
        from flask_mysqldb import MySQL
        import MySQLdb.cursors
        
        app = Flask(__name__)
        app.config['MYSQL_HOST'] = '127.0.0.1'
        app.config['MYSQL_PORT'] = 3307
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = ''
        app.config['MYSQL_DB'] = 'digital_carbon_tracker'
        app.config['MYSQL_CURSORCLASS'] = MySQLdb.cursors.DictCursor
        
        mysql = MySQL(app)
        cursor = mysql.connection.cursor()
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        cursor.close()
        
        column_names = [col[0] for col in columns]
        
        if 'google_id' in column_names:
            print("✅ Database has google_id column")
            return True
        else:
            print("❌ Database is missing google_id column")
            print("\nRun this SQL to add the column:")
            print("   ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE DEFAULT NULL;")
            return False
    except Exception as e:
        print(f"⚠️  Could not check database: {e}")
        return False

def main():
    print("=" * 60)
    print("CarbonTracker Google OAuth 2.0 Setup Check")
    print("=" * 60)
    print()
    
    checks = [
        ("Environment Configuration", check_env_file),
        ("Dependencies", check_dependencies),
        ("Database Schema", check_database)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        print("-" * 60)
        result = check_func()
        results.append((check_name, result))
        print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    print()
    if all_passed:
        print("🎉 All checks passed! You're ready to use Google OAuth.")
        print("\nNext steps:")
        print("1. Start your Flask app: python app.py")
        print("2. Visit http://localhost:5000/login")
        print("3. Click 'Continue with Google'")
        print("4. Select your Google account")
        print("\nFor production deployment, see GOOGLE_OAUTH_SETUP.md")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor detailed setup instructions, see GOOGLE_OAUTH_SETUP.md")
        return 1

if __name__ == '__main__':
    sys.exit(main())
