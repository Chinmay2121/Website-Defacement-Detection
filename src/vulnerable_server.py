"""
Enhanced Dynamic Vulnerable Web Server with Dark Theme & Eye-Tracking
EDUCATIONAL PURPOSE ONLY - Contains intentional security vulnerabilities
NEW FEATURES:
- Dark black and grey theme
- Animated face emoji that follows cursor
- Dynamic sliding vulnerability showcase
- Smooth animations and effects
"""

from flask import Flask, render_template_string, request, redirect, jsonify, send_from_directory, url_for
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib
import base64

app = Flask(__name__)
app.secret_key = 'insecure_demo_key_12345'

app.config['WTF_CSRF_ENABLED'] = False
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
UPLOADS_DIR = DATA_DIR / 'uploads'

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

CONTENT_FILE = DATA_DIR / 'website_content.json'
CHANGE_LOG_FILE = LOGS_DIR / 'change_log.json'
DB_FILE = DATA_DIR / 'website.db'


def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM posts')
    if cursor.fetchone()[0] == 0:
        initial_posts = [
            ('Welcome to SecureDemo Corp', 
             'We are excited to launch our new website! Stay tuned for updates on our latest cybersecurity solutions.',
             'Admin'),
            ('Cybersecurity Best Practices',
             'Learn about the importance of regular security audits and monitoring systems to protect your digital assets.',
             'Security Team'),
        ]
        cursor.executemany(
            'INSERT INTO posts (title, content, author) VALUES (?, ?, ?)',
            initial_posts
        )
    
    conn.commit()
    conn.close()


def init_content():
    """Initialize website content"""
    default_content = {
        'homepage_title': 'Welcome to SecureDemo Corp',
        'homepage_content': '''
            <h2>Professional Business Solutions</h2>
            <p>We provide cutting-edge technology solutions for modern businesses.</p>
            <ul>
                <li>Cloud Infrastructure</li>
                <li>Cybersecurity Services</li>
                <li>Enterprise Software</li>
            </ul>
        ''',
        'about_content': '''
            <h2>About Us</h2>
            <p>SecureDemo Corp has been serving clients since 2020.</p>
            <p>Our mission is to deliver secure and reliable technology solutions.</p>
        ''',
        'logo_filename': 'company_logo.png',
        'last_modified': datetime.now().isoformat()
    }
    
    if not CONTENT_FILE.exists():
        save_content(default_content, log_change=False)
    
    logo_path = UPLOADS_DIR / 'company_logo.png'
    if not logo_path.exists():
        placeholder = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        logo_path.write_bytes(placeholder)
    
    if not CHANGE_LOG_FILE.exists():
        CHANGE_LOG_FILE.write_text('', encoding='utf-8')
    
    return load_content()


def load_content():
    """Load content from JSON file"""
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return init_content()


def save_content(content, log_change=True):
    """Save content to JSON file"""
    try:
        old_content = load_content() if log_change else None
        content['last_modified'] = datetime.now().isoformat()
        
        if log_change and old_content:
            old_without_time = {k: v for k, v in old_content.items() 
                               if k != 'last_modified'}
            new_without_time = {k: v for k, v in content.items() 
                               if k != 'last_modified'}
            
            if old_without_time != new_without_time:
                log_content_change(old_content, content)
        
        temp_file = CONTENT_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        temp_file.replace(CONTENT_FILE)
        return True
    except Exception as e:
        print(f"❌ Error saving content: {e}")
        return False


def log_content_change(old_content, new_content):
    """Log content changes"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr if request else 'system',
        'user_agent': request.headers.get('User-Agent', 'N/A') if request else 'N/A',
        'changes': {}
    }
    
    for key in new_content:
        if key == 'last_modified':
            continue
        old_val = old_content.get(key, '')
        new_val = new_content.get(key, '')
        if old_val != new_val:
            log_entry['changes'][key] = {
                'old': old_val[:100] + '...' if len(str(old_val)) > 100 else old_val,
                'new': new_val[:100] + '...' if len(str(new_val)) > 100 else new_val
            }
    
    try:
        with open(CHANGE_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"⚠️ Error logging change: {e}")


def get_image_hash(filename):
    """Calculate hash of an image file"""
    filepath = UPLOADS_DIR / filename
    if not filepath.exists():
        return None
    
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)
    return sha256.hexdigest()


# Dark Theme Template with Eye-Tracking Face
DARK_EYE_TRACKING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Dark Security Lab</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #e0e0e0;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
            min-height: 100vh;
            overflow-x: hidden;
            cursor: default;
        }
        
        /* Custom Cursor Style */
        * {
            cursor: default;
        }
        
        a, button, .slider-dot {
            cursor: pointer !important;
        }
        
        input, textarea {
            cursor: text !important;
        }
        
        /* Eye-Tracking Devil Face Container 😈 */
        .face-container {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 120px;
            height: 120px;
            z-index: 10000;
            pointer-events: none;
            filter: drop-shadow(0 0 20px rgba(255, 0, 0, 0.6));
        }
        
        .face {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #8B0000, #FF0000);
            border-radius: 50%;
            position: relative;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.4);
            animation: faceBounce 3s ease-in-out infinite;
        }
        
        @keyframes faceBounce {
            0%, 100% { transform: translateY(0) rotate(-5deg); }
            50% { transform: translateY(-10px) rotate(5deg); }
        }
        
        /* Devil Horns */
        .horn {
            position: absolute;
            width: 20px;
            height: 30px;
            background: linear-gradient(135deg, #600000, #8B0000);
            border-radius: 5px 5px 0 0;
            top: -15px;
        }
        
        .horn.left {
            left: 20px;
            transform: rotate(-20deg);
        }
        
        .horn.right {
            right: 20px;
            transform: rotate(20deg);
        }
        
        .eye {
            position: absolute;
            width: 25px;
            height: 25px;
            background: #FFD700;
            border-radius: 50%;
            top: 35px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.3);
        }
        
        .eye.left { left: 25px; }
        .eye.right { right: 25px; }
        
        .pupil {
            position: absolute;
            width: 12px;
            height: 12px;
            background: #000;
            border-radius: 50%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            transition: all 0.1s ease-out;
        }
        
        .mouth {
            position: absolute;
            width: 50px;
            height: 25px;
            border: 3px solid #000;
            border-top: none;
            border-radius: 0 0 50px 50px;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            transition: all 0.3s ease;
            background: rgba(0, 0, 0, 0.2);
        }
        
        /* Evil grin */
        .mouth::before {
            content: '';
            position: absolute;
            width: 8px;
            height: 12px;
            background: white;
            border-radius: 2px;
            left: 8px;
            top: -3px;
            box-shadow: 10px 0 0 white, 20px 0 0 white, 30px 0 0 white;
        }
        
        .face:hover .mouth {
            height: 30px;
            border-radius: 0 0 60px 60px;
        }
        
        /* Devil tail */
        .tail {
            position: absolute;
            width: 4px;
            height: 40px;
            background: linear-gradient(180deg, #8B0000, #600000);
            bottom: -35px;
            left: 50%;
            transform: translateX(-50%) rotate(20deg);
            border-radius: 2px;
        }
        
        .tail::after {
            content: '';
            position: absolute;
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 12px solid #600000;
            bottom: -10px;
            left: -6px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 10;
        }
        
        /* Dark Header */
        header {
            background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
            backdrop-filter: blur(10px);
            color: #e0e0e0;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.7);
            border: 1px solid #3a3a3a;
            animation: slideDown 0.8s ease-out;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .header-content {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: #333;
            border-radius: 10px;
            padding: 10px;
            object-fit: contain;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: transform 0.3s ease;
            border: 2px solid #555;
        }
        
        .logo:hover {
            transform: scale(1.1) rotate(5deg);
            border-color: #FFD700;
        }
        
        h1 {
            flex: 1;
            font-size: 2.5em;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: textGlow 3s ease infinite;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }
        
        @keyframes textGlow {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.3); }
        }
        
        .nav {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .nav a {
            color: #FFD700;
            text-decoration: none;
            padding: 10px 20px;
            background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%);
            border-radius: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            border: 1px solid #555;
        }
        
        .nav a:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
            background: linear-gradient(135deg, #4a4a4a 0%, #3a3a3a 100%);
            border-color: #FFD700;
        }
        
        .nav a.admin {
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: white;
            border-color: #ff6666;
        }
        
        .nav a.admin:hover {
            box-shadow: 0 6px 20px rgba(255, 68, 68, 0.4);
        }
        
        /* Vulnerability Showcase */
        .vulnerability-showcase {
            background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.7);
            border: 1px solid #3a3a3a;
            position: relative;
            overflow: hidden;
            min-height: 400px;
        }
        
        .showcase-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .showcase-header h2 {
            color: #FFD700;
            font-size: 2em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        }
        
        .showcase-header p {
            color: #999;
        }
        
        .vulnerability-slider {
            position: relative;
            height: 300px;
        }
        
        .vulnerability-slide {
            position: absolute;
            width: 100%;
            height: 100%;
            opacity: 0;
            transition: opacity 0.8s ease-in-out;
            padding: 20px;
        }
        
        .vulnerability-slide.active {
            opacity: 1;
            animation: slideIn 0.8s ease-out;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .vuln-card {
            background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%);
            border-radius: 15px;
            padding: 30px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border-left: 5px solid;
            transition: transform 0.3s ease;
            box-shadow: 0 5px 20px rgba(0,0,0,0.5);
        }
        
        .vuln-card:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 30px rgba(0,0,0,0.7);
        }
        
        .vuln-card.critical { border-left-color: #ff4444; }
        .vuln-card.high { border-left-color: #ff9944; }
        .vuln-card.medium { border-left-color: #ffcc44; }
        
        .vuln-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .vuln-icon {
            font-size: 3em;
            animation: bounce 2s infinite;
            filter: drop-shadow(0 0 10px currentColor);
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .vuln-title {
            font-size: 1.8em;
            color: #FFD700;
            font-weight: bold;
        }
        
        .vuln-severity {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .severity-critical {
            background: #ff4444;
            color: white;
            box-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
        }
        
        .severity-high {
            background: #ff9944;
            color: white;
            box-shadow: 0 0 10px rgba(255, 153, 68, 0.5);
        }
        
        .severity-medium {
            background: #ffcc44;
            color: #333;
            box-shadow: 0 0 10px rgba(255, 204, 68, 0.5);
        }
        
        .vuln-description {
            font-size: 1.1em;
            color: #bbb;
            margin: 15px 0;
            line-height: 1.8;
        }
        
        .vuln-demo {
            background: rgba(0, 0, 0, 0.4);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #FFD700;
            border: 1px solid #555;
        }
        
        .slider-controls {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .slider-dot {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: #555;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid #777;
        }
        
        .slider-dot.active {
            background: #FFD700;
            transform: scale(1.3);
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
        }
        
        .slider-dot:hover {
            background: #FFA500;
            border-color: #FFD700;
        }
        
        /* Progress Bar */
        .progress-bar {
            height: 4px;
            background: #333;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 20px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
            width: 0%;
            animation: progress 5s linear infinite;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.6);
        }
        
        @keyframes progress {
            0% { width: 0%; }
            100% { width: 100%; }
        }
        
        /* Stats Dashboard */
        .stats-dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.7);
            border: 1px solid #3a3a3a;
            text-align: center;
            transition: transform 0.3s ease;
            animation: fadeIn 1s ease-out;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: #FFD700;
            box-shadow: 0 15px 50px rgba(0,0,0,0.9);
        }
        
        .stat-icon {
            font-size: 3em;
            margin-bottom: 10px;
            filter: drop-shadow(0 0 10px currentColor);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #FFD700;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        }
        
        .stat-label {
            color: #999;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 1px;
        }
        
        /* Content Section */
        .content {
            background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.7);
            border: 1px solid #3a3a3a;
            margin-bottom: 30px;
            animation: fadeIn 1s ease-out;
        }
        
        .content h2 {
            color: #FFD700;
            margin: 25px 0 15px 0;
        }
        
        .content p, .content li {
            color: #bbb;
        }
        
        /* Image Gallery */
        .image-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .gallery-item {
            background: #333;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            border: 1px solid #444;
        }
        
        .gallery-item:hover {
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
            border-color: #FFD700;
        }
        
        .gallery-item img {
            max-width: 100%;
            max-height: 150px;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid #555;
        }
        
        .gallery-item div {
            color: #bbb;
            font-size: 0.9em;
            margin: 5px 0;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            h1 { font-size: 1.8em; }
            .vulnerability-slider { height: auto; min-height: 400px; }
            .vuln-icon { font-size: 2em; }
            .vuln-title { font-size: 1.4em; }
            .face-container {
                width: 80px;
                height: 80px;
                top: 10px;
                right: 10px;
            }
        }
    </style>
</head>
<body>
    <!-- Eye-Tracking Devil Face 😈 -->
    <div class="face-container">
        <div class="face">
            <div class="horn left"></div>
            <div class="horn right"></div>
            <div class="eye left">
                <div class="pupil" id="leftPupil"></div>
            </div>
            <div class="eye right">
                <div class="pupil" id="rightPupil"></div>
            </div>
            <div class="mouth"></div>
            <div class="tail"></div>
        </div>
    </div>
    
    <div class="container">
        <header>
            <div class="header-content">
                <img src="{{ url_for('get_upload', filename=logo_filename) }}" alt="Logo" class="logo">
                <div style="flex: 1;">
                    <h1>{{ title }}</h1>
                    <p style="color: #999; margin-top: 10px;">🎓 Dark Security Research Laboratory</p>
                </div>
            </div>
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/about">ℹ️ About</a>
                <a href="/blog">📝 Blog</a>
                <a href="/admin" class="admin">🔧 Admin Panel</a>
            </div>
        </header>
        
        <!-- Vulnerability Showcase Slider -->
        <div class="vulnerability-showcase">
            <div class="showcase-header">
                <h2>🚨 Live Vulnerability Showcase</h2>
                <p>Automatic demonstration of common web security vulnerabilities</p>
            </div>
            
            <div class="vulnerability-slider" id="vulnerabilitySlider">
                <!-- Slide 1: XSS -->
                <div class="vulnerability-slide active" data-slide="0">
                    <div class="vuln-card critical">
                        <div class="vuln-header">
                            <div class="vuln-icon">🔓</div>
                            <div>
                                <div class="vuln-title">Cross-Site Scripting (XSS)</div>
                                <span class="vuln-severity severity-critical">Critical</span>
                            </div>
                        </div>
                        <div class="vuln-description">
                            Malicious scripts can be injected into web pages viewed by other users.
                            This allows attackers to steal cookies, session tokens, or redirect users to malicious sites.
                        </div>
                        <div class="vuln-demo">
                            <strong>Example Attack:</strong><br>
                            &lt;script&gt;alert('XSS Vulnerability!')&lt;/script&gt;
                        </div>
                        <div style="color: #ff4444; font-weight: bold;">
                            ⚠️ Detection System monitors for script injection patterns
                        </div>
                    </div>
                </div>
                
                <!-- Slide 2: No Authentication -->
                <div class="vulnerability-slide" data-slide="1">
                    <div class="vuln-card critical">
                        <div class="vuln-header">
                            <div class="vuln-icon">🚪</div>
                            <div>
                                <div class="vuln-title">No Authentication</div>
                                <span class="vuln-severity severity-critical">Critical</span>
                            </div>
                        </div>
                        <div class="vuln-description">
                            Admin panel accessible without any login credentials.
                            Anyone can modify website content, upload files, and change configurations.
                        </div>
                        <div class="vuln-demo">
                            <strong>Impact:</strong><br>
                            • Unauthorized content modification<br>
                            • Data breach<br>
                            • Complete website takeover
                        </div>
                        <div style="color: #ff4444; font-weight: bold;">
                            ⚠️ Detection System alerts on unauthorized content changes
                        </div>
                    </div>
                </div>
                
                <!-- Slide 3: File Upload Vulnerability -->
                <div class="vulnerability-slide" data-slide="2">
                    <div class="vuln-card high">
                        <div class="vuln-header">
                            <div class="vuln-icon">📁</div>
                            <div>
                                <div class="vuln-title">Unrestricted File Upload</div>
                                <span class="vuln-severity severity-high">High</span>
                            </div>
                        </div>
                        <div class="vuln-description">
                            No validation on uploaded files allows malicious file uploads.
                            Attackers can upload executable files, shell scripts, or replace legitimate images.
                        </div>
                        <div class="vuln-demo">
                            <strong>Attack Vector:</strong><br>
                            Upload malicious image with embedded code<br>
                            Replace company logo with defacement image
                        </div>
                        <div style="color: #ff9944; font-weight: bold;">
                            ⚠️ Detection System monitors image integrity via hash comparison
                        </div>
                    </div>
                </div>
                
                <!-- Slide 4: SQL Injection -->
                <div class="vulnerability-slide" data-slide="3">
                    <div class="vuln-card high">
                        <div class="vuln-header">
                            <div class="vuln-icon">💉</div>
                            <div>
                                <div class="vuln-title">SQL Injection</div>
                                <span class="vuln-severity severity-high">High</span>
                            </div>
                        </div>
                        <div class="vuln-description">
                            Database queries vulnerable to SQL injection attacks.
                            Attackers can manipulate queries to access, modify, or delete database records.
                        </div>
                        <div class="vuln-demo">
                            <strong>Example Attack:</strong><br>
                            ' OR '1'='1' --<br>
                            '; DROP TABLE users; --
                        </div>
                        <div style="color: #ff9944; font-weight: bold;">
                            ⚠️ Detection System monitors database activity
                        </div>
                    </div>
                </div>
                
                <!-- Slide 5: No CSRF Protection -->
                <div class="vulnerability-slide" data-slide="4">
                    <div class="vuln-card medium">
                        <div class="vuln-header">
                            <div class="vuln-icon">🎣</div>
                            <div>
                                <div class="vuln-title">CSRF Vulnerability</div>
                                <span class="vuln-severity severity-medium">Medium</span>
                            </div>
                        </div>
                        <div class="vuln-description">
                            No Cross-Site Request Forgery protection on forms.
                            Attackers can trick users into performing unwanted actions while authenticated.
                        </div>
                        <div class="vuln-demo">
                            <strong>Attack Scenario:</strong><br>
                            Malicious website sends authenticated requests<br>
                            to change user settings or post content
                        </div>
                        <div style="color: #ffcc44; font-weight: bold;">
                            ⚠️ Detection System logs all state-changing requests
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="slider-controls">
                <span class="slider-dot active" data-slide="0"></span>
                <span class="slider-dot" data-slide="1"></span>
                <span class="slider-dot" data-slide="2"></span>
                <span class="slider-dot" data-slide="3"></span>
                <span class="slider-dot" data-slide="4"></span>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
        
        <!-- Stats Dashboard -->
        <div class="stats-dashboard">
            <div class="stat-card">
                <div class="stat-icon">🔍</div>
                <div class="stat-value">5</div>
                <div class="stat-label">Vulnerabilities Demonstrated</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🛡️</div>
                <div class="stat-value">Real-time</div>
                <div class="stat-label">Detection Active</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">100%</div>
                <div class="stat-label">Educational Purpose</div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="content">
            {{ content|safe }}
            
            <hr style="margin: 30px 0; border: none; border-top: 2px solid #444;">
            
            <h2>🖼️ Monitored Images</h2>
            <div class="image-gallery">
                {% for image in images %}
                <div class="gallery-item">
                    <img src="{{ url_for('get_upload', filename=image['filename']) }}" alt="{{ image['filename'] }}">
                    <div style="font-weight: bold; color: #FFD700;">{{ image['filename'] }}</div>
                    <div style="color: #999; font-size: 0.85em;">
                        Hash: {{ image['hash'][:12] }}...
                    </div>
                    <div style="color: #6c6; font-size: 0.8em; margin-top: 5px;">
                        ✓ Integrity Monitored
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        // Eye-Tracking Functionality
        const leftPupil = document.getElementById('leftPupil');
        const rightPupil = document.getElementById('rightPupil');
        const leftEye = document.querySelector('.eye.left');
        const rightEye = document.querySelector('.eye.right');
        
        document.addEventListener('mousemove', (e) => {
            const mouseX = e.clientX;
            const mouseY = e.clientY;
            
            // Left Eye
            const leftEyeRect = leftEye.getBoundingClientRect();
            const leftEyeX = leftEyeRect.left + leftEyeRect.width / 2;
            const leftEyeY = leftEyeRect.top + leftEyeRect.height / 2;
            
            const leftAngle = Math.atan2(mouseY - leftEyeY, mouseX - leftEyeX);
            const leftDistance = Math.min(6, Math.hypot(mouseX - leftEyeX, mouseY - leftEyeY) / 50);
            
            const leftPupilX = Math.cos(leftAngle) * leftDistance;
            const leftPupilY = Math.sin(leftAngle) * leftDistance;
            
            leftPupil.style.transform = `translate(calc(-50% + ${leftPupilX}px), calc(-50% + ${leftPupilY}px))`;
            
            // Right Eye
            const rightEyeRect = rightEye.getBoundingClientRect();
            const rightEyeX = rightEyeRect.left + rightEyeRect.width / 2;
            const rightEyeY = rightEyeRect.top + rightEyeRect.height / 2;
            
            const rightAngle = Math.atan2(mouseY - rightEyeY, mouseX - rightEyeX);
            const rightDistance = Math.min(6, Math.hypot(mouseX - rightEyeX, mouseY - rightEyeY) / 50);
            
            const rightPupilX = Math.cos(rightAngle) * rightDistance;
            const rightPupilY = Math.sin(rightAngle) * rightDistance;
            
            rightPupil.style.transform = `translate(calc(-50% + ${rightPupilX}px), calc(-50% + ${rightPupilY}px))`;
        });
        
        // Vulnerability Slider Logic
        let currentSlide = 0;
        const slides = document.querySelectorAll('.vulnerability-slide');
        const dots = document.querySelectorAll('.slider-dot');
        const slideInterval = 5000;
        
        function showSlide(n) {
            slides.forEach(slide => slide.classList.remove('active'));
            dots.forEach(dot => dot.classList.remove('active'));
            
            currentSlide = (n + slides.length) % slides.length;
            slides[currentSlide].classList.add('active');
            dots[currentSlide].classList.add('active');
        }
        
        function nextSlide() {
            showSlide(currentSlide + 1);
        }
        
        let autoAdvance = setInterval(nextSlide, slideInterval);
        
        dots.forEach(dot => {
            dot.addEventListener('click', function() {
                const slideNum = parseInt(this.getAttribute('data-slide'));
                showSlide(slideNum);
                clearInterval(autoAdvance);
                autoAdvance = setInterval(nextSlide, slideInterval);
            });
        });
        
        const slider = document.getElementById('vulnerabilitySlider');
        slider.addEventListener('mouseenter', () => {
            clearInterval(autoAdvance);
        });
        
        slider.addEventListener('mouseleave', () => {
            autoAdvance = setInterval(nextSlide, slideInterval);
        });
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    """Dark themed homepage with eye-tracking face"""
    content = load_content()
    images = []
    for filepath in UPLOADS_DIR.iterdir():
        if filepath.is_file():
            images.append({
                'filename': filepath.name,
                'hash': get_image_hash(filepath.name)
            })
    return render_template_string(
        DARK_EYE_TRACKING_TEMPLATE,
        title=content['homepage_title'],
        content=content['homepage_content'],
        logo_filename=content.get('logo_filename', 'company_logo.png'),
        images=images
    )


@app.route('/about')
def about():
    """About page"""
    content = load_content()
    return render_template_string(
        DARK_EYE_TRACKING_TEMPLATE,
        title='About Us',
        content=content['about_content'],
        logo_filename=content.get('logo_filename', 'company_logo.png'),
        images=[]
    )


@app.route('/blog')
def blog():
    """Blog page"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
    posts = []
    for post_row in cursor.fetchall():
        post = dict(post_row)
        cursor.execute(
            'SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC',
            (post['id'],)
        )
        post['comments'] = [dict(row) for row in cursor.fetchall()]
        post['comment_count'] = len(post['comments'])
        posts.append(post)
    
    conn.close()
    
    # Dark themed blog template
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>BLOG</title>
    <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%); color: #e0e0e0; padding: 20px; min-height: 100vh; }
    .container { max-width: 1000px; margin: 0 auto; }
    header { background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid #3a3a3a; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.7); }
    h1 { color: #FFD700; text-shadow: 0 0 20px rgba(255,215,0,0.5); font-size: 2.5em; }
    .nav { display: flex; gap: 15px; margin-top: 20px; }
    .nav a { color: #FFD700; text-decoration: none; padding: 10px 20px; background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%); border: 1px solid #555; border-radius: 25px; transition: all 0.3s; }
    .nav a:hover { border-color: #FFD700; box-shadow: 0 6px 20px rgba(255,215,0,0.4); transform: translateY(-2px); }
    .post { background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid #3a3a3a; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.7); }
    .post h2 { color: #FFD700; text-shadow: 0 0 10px rgba(255,215,0,0.5); margin-bottom: 10px; }
    .post-meta { color: #999; font-size: 0.9em; margin-bottom: 15px; }
    .post p { color: #bbb; }
    .comment-section { margin-top: 30px; padding-top: 20px; border-top: 2px solid #444; }
    .comment { background: rgba(0,0,0,0.3); padding: 15px; margin: 15px 0; border-radius: 10px; border-left: 3px solid #FFD700; }
    .comment-author { font-weight: bold; color: #FFD700; }
    .comment-form input, .comment-form textarea { width: 100%; padding: 10px; margin-bottom: 10px; background: rgba(0,0,0,0.4); border: 2px solid #555; border-radius: 5px; color: #e0e0e0; font-family: inherit; }
    .comment-form input:focus, .comment-form textarea:focus { outline: none; border-color: #FFD700; box-shadow: 0 0 10px rgba(255,215,0,0.3); }
    .comment-form button { background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%); color: #FFD700; padding: 10px 25px; border: 1px solid #555; border-radius: 25px; cursor: pointer; transition: all 0.3s; }
    .comment-form button:hover { border-color: #FFD700; box-shadow: 0 6px 20px rgba(255,215,0,0.4); transform: translateY(-2px); }
    </style>
    </head><body>
    <div class="container">
        <header><h1>📝 BLOG SYSTEM</h1>
        <div class="nav">
            <a href="/">🏠 HOME</a><a href="/about">ℹ️ ABOUT</a><a href="/admin">🔧 ADMIN</a>
        </div></header>
        {% for post in posts %}
        <div class="post">
            <h2>{{ post.title }}</h2>
            <div class="post-meta">BY {{ post.author }} • {{ post.created_at }}</div>
            <p>{{ post.content }}</p>
            <div class="comment-section">
                <h3 style="color: #FFD700;">COMMENTS ({{ post.comment_count }})</h3>
                {% for comment in post.comments %}
                <div class="comment">
                    <div class="comment-author">{{ comment.author }}</div>
                    <div style="color: #bbb;">{{ comment.content }}</div>
                    <small style="color:#666;">{{ comment.created_at }}</small>
                </div>
                {% endfor %}
                <form method="POST" action="/blog/comment/{{ post.id }}" class="comment-form">
                    <h4 style="color: #FFD700;">LEAVE COMMENT</h4>
                    <input type="text" name="author" placeholder="Your Name" required>
                    <textarea name="content" placeholder="Your Comment" rows="3" required></textarea>
                    <button type="submit">POST COMMENT</button>
                </form>
            </div>
        </div>
        {% endfor %}
    </div></body></html>
    """, posts=posts)


@app.route('/blog/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    """Add comment"""
    author = request.form.get('author', 'Anonymous')
    content = request.form.get('content', '')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)',
        (post_id, author, content)
    )
    conn.commit()
    conn.close()
    
    return redirect('/blog')


@app.route('/admin')
def admin():
    """Admin panel"""
    content = load_content()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>ADMIN PANEL</title>
    <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%); color: #e0e0e0; min-height: 100vh; padding: 20px; }
    .container { max-width: 1000px; margin: 0 auto; background: linear-gradient(135deg, #2a2a2a 0%, #1f1f1f 100%); border: 1px solid #3a3a3a; border-radius: 15px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.7); }
    h1 { color: #FFD700; text-shadow: 0 0 20px rgba(255,215,0,0.5); margin-bottom: 20px; font-size: 2.5em; }
    h2 { color: #FFD700; text-shadow: 0 0 10px rgba(255,215,0,0.5); margin-top: 30px; margin-bottom: 15px; }
    .nav { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #444; }
    .nav a { color: #FFD700; text-decoration: none; margin-right: 20px; padding: 8px 16px; background: rgba(0,0,0,0.3); border: 1px solid #555; border-radius: 8px; transition: all 0.3s; }
    .nav a:hover { border-color: #FFD700; box-shadow: 0 0 15px rgba(255,215,0,0.3); }
    .warning { background: rgba(255,200,0,0.1); border-left: 4px solid #ffaa00; padding: 20px; margin: 20px 0; border-radius: 10px; color: #ffcc66; }
    .section { background: rgba(0,0,0,0.3); padding: 25px; border-radius: 15px; margin: 20px 0; border: 1px solid #444; }
    .form-group { margin: 25px 0; }
    label { display: block; margin-bottom: 8px; font-weight: 600; color: #FFD700; }
    input[type="text"], textarea, input[type="file"] { width: 100%; padding: 12px; background: rgba(0,0,0,0.5); border: 2px solid #555; border-radius: 8px; color: #e0e0e0; font-family: inherit; font-size: 14px; }
    input:focus, textarea:focus { outline: none; border-color: #FFD700; box-shadow: 0 0 15px rgba(255,215,0,0.3); }
    textarea { min-height: 120px; resize: vertical; }
    button { background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%); color: #FFD700; padding: 12px 30px; border: 1px solid #555; border-radius: 25px; cursor: pointer; font-size: 16px; font-weight: 600; margin-top: 10px; transition: all 0.3s; }
    button:hover { border-color: #FFD700; box-shadow: 0 6px 20px rgba(255,215,0,0.4); transform: translateY(-2px); }
    .current-logo { max-width: 200px; margin: 10px 0; border: 2px solid #555; border-radius: 10px; padding: 10px; background: rgba(0,0,0,0.5); }
    </style>
    </head><body>
    <div class="container">
        <div class="nav">
            <a href="/">← BACK TO HOME</a><a href="/blog">BLOG</a>
        </div>
        <h1>🔧 ADMIN CONTROL PANEL</h1>
        <div class="warning">
            <strong>⚠️ INTENTIONAL SECURITY VULNERABILITIES:</strong>
            <ul style="margin: 10px 0 0 20px;">
                <li>❌ NO AUTHENTICATION REQUIRED</li>
                <li>❌ NO INPUT SANITIZATION (XSS VULNERABLE)</li>
                <li>❌ NO CSRF PROTECTION</li>
                <li>❌ NO FILE UPLOAD VALIDATION</li>
                <li>❌ ALL CHANGES ARE LOGGED & MONITORED</li>
            </ul>
        </div>
        <form method="POST" action="/admin/update" enctype="multipart/form-data">
            <div class="section">
                <h2>🖼️ LOGO MANAGEMENT</h2>
                <div class="form-group">
                    <label>CURRENT LOGO:</label>
                    <img src="{{ url_for('get_upload', filename=content.logo_filename) }}" alt="Logo" class="current-logo">
                </div>
                <div class="form-group">
                    <label>UPLOAD NEW LOGO:</label>
                    <input type="file" name="logo" accept="image/*">
                </div>
            </div>
            <div class="section">
                <h2>📝 CONTENT MANAGEMENT</h2>
                <div class="form-group">
                    <label>HOMEPAGE TITLE:</label>
                    <input type="text" name="homepage_title" value="{{ content.homepage_title }}" required>
                </div>
                <div class="form-group">
                    <label>HOMEPAGE CONTENT (HTML ALLOWED - XSS VULNERABLE!):</label>
                    <textarea name="homepage_content" required>{{ content.homepage_content }}</textarea>
                </div>
                <div class="form-group">
                    <label>ABOUT PAGE CONTENT:</label>
                    <textarea name="about_content" required>{{ content.about_content }}</textarea>
                </div>
            </div>
            <button type="submit">💾 UPDATE WEBSITE</button>
        </form>
        <div class="section">
            <h2>📝 ADD BLOG POST</h2>
            <form method="POST" action="/admin/add_post">
                <div class="form-group">
                    <label>POST TITLE:</label>
                    <input type="text" name="title" required>
                </div>
                <div class="form-group">
                    <label>CONTENT:</label>
                    <textarea name="content" required></textarea>
                </div>
                <div class="form-group">
                    <label>AUTHOR:</label>
                    <input type="text" name="author" required>
                </div>
                <button type="submit">ADD POST</button>
            </form>
        </div>
    </div></body></html>
    """, content=content)


@app.route('/admin/update', methods=['POST'])
def admin_update():
    """Update website content and logo"""
    try:
        content = load_content()
        
        if 'homepage_title' in request.form:
            content['homepage_title'] = request.form['homepage_title']
        if 'homepage_content' in request.form:
            content['homepage_content'] = request.form['homepage_content']
        if 'about_content' in request.form:
            content['about_content'] = request.form['about_content']
        
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file.filename:
                filename = logo_file.filename
                logo_path = UPLOADS_DIR / filename
                logo_file.save(logo_path)
                content['logo_filename'] = filename
        
        save_content(content)
        return redirect('/')
        
    except Exception as e:
        print(f"❌ Error in admin_update: {e}")
        return redirect('/admin')


@app.route('/admin/add_post', methods=['POST'])
def add_post():
    """Add blog post"""
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    author = request.form.get('author', 'Anonymous')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO posts (title, content, author) VALUES (?, ?, ?)',
        (title, content, author)
    )
    conn.commit()
    conn.close()
    
    return redirect('/blog')


@app.route('/uploads/<path:filename>')
def get_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOADS_DIR, filename)


@app.route('/api/content')
def api_content():
    """API endpoint for monitoring"""
    content = load_content()
    logo_filename = content.get('logo_filename', 'company_logo.png')
    content['logo_hash'] = get_image_hash(logo_filename)
    response = jsonify(content)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/images')
def api_images():
    """API endpoint to list all images"""
    images = []
    for filepath in UPLOADS_DIR.iterdir():
        if filepath.is_file():
            images.append({
                'filename': filepath.name,
                'hash': get_image_hash(filepath.name),
                'size': filepath.stat().st_size
            })
    response = jsonify({'images': images})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    response = jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def main():
    """Main entry point"""
    init_database()
    init_content()
    
    print("\n" + "="*70)
    print("👁️  DARK THEME WITH EYE-TRACKING FACE EMOJI 👁️")
    print("="*70)
    print("\n🌐 Server Information:")
    print(f"   URL: http://localhost:5000")
    print("\n🔗 Available Endpoints:")
    print("   Home:  http://localhost:5000/")
    print("   Admin: http://localhost:5000/admin")
    print("   Blog:  http://localhost:5000/blog")
    print("\n🎨 NEW FEATURES:")
    print("   ✓ Dark black & grey theme")
    print("   ✓ Animated face emoji that follows your cursor")
    print("   ✓ Eye-tracking pupils that look at mouse position")
    print("   ✓ Golden accent colors (#FFD700)")
    print("   ✓ Smooth animations and hover effects")
    print("   ✓ Auto-rotating vulnerability showcase")
    print("\n⛔ FOR EDUCATIONAL USE ONLY")
    print("="*70 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)


if __name__ == '__main__':
    main()