<<<<<<< HEAD
# Website-Defacement-Detection
=======
# Website Defacement Detection System

A comprehensive educational project demonstrating website defacement detection techniques using real-time file monitoring, content integrity checking, and alert systems.

## 🎓 Educational Purpose

This project is designed for **educational purposes only** to understand:
- How website defacement attacks work
- How to detect unauthorized changes
- Security monitoring and alerting systems
- Common web vulnerabilities

**⚠️ WARNING: Never use on production systems or without authorization!**

## 🏗️ Project Structure

```
defacement-detection-system/
├── src/
│   ├── vulnerable_server.py      # Intentionally vulnerable web server
│   ├── detection_monitor.py      # Detection and monitoring system
│   └── attack_simulator.py       # Attack simulation tool
├── data/
│   ├── website_content.json      # Website content (auto-generated)
│   └── baseline.json             # Detection baseline (auto-generated)
├── logs/
│   ├── change_log.json           # Change history (auto-generated)
│   ├── defacement_alerts.json    # Alert log (auto-generated)
│   └── detection_log.txt         # Human-readable log (auto-generated)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## ⚙️ System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 512MB minimum
- **Disk Space**: 100MB

## 🚀 Installation & Setup

### Step 1: Clone or Download Project

```bash
# Create project directory
mkdir defacement-detection-system
cd defacement-detection-system

# Create subdirectories
mkdir src data logs
```

### Step 2: Create Virtual Environment

**Windows (Command Prompt or PowerShell):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate.bat
```

**Verify activation:** Your terminal should show `(venv)` prefix

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**If requirements.txt doesn't exist, install manually:**
```bash
pip install flask requests watchdog colorama
```

### Step 4: Place Files

Copy the provided Python files into the `src/` directory:
- `vulnerable_server.py`
- `detection_monitor.py`
- `attack_simulator.py`

## 📖 Usage Guide

### Running the System

You'll need **three terminal windows** (all with activated virtual environment):

#### Terminal 1: Start Vulnerable Server

```bash
# Activate venv first
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Run server
python src/vulnerable_server.py
```

**Expected output:**
```
🚨 VULNERABLE WEB SERVER - EDUCATIONAL DEMO ONLY
Server running at: http://localhost:5000
```

#### Terminal 2: Start Detection Monitor

```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Run monitor
python src/detection_monitor.py
```

**First time setup:**
1. Choose option `1` (Create new baseline)
2. Choose `yes` to start monitoring

**Subsequent runs:**
- Choose option `2` (Load existing baseline and monitor)

#### Terminal 3: Simulate Attacks

```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Run attack simulator
python src/attack_simulator.py
```

**Available attacks:**
1. Simple Defacement
2. XSS Injection
3. Subtle Defacement
4. Redirect Injection
5. Phishing Page
6. Crypto Miner Injection
7. Restore Original Content

## 🎯 How It Works

### 1. Vulnerable Server (`vulnerable_server.py`)

**Intentional Vulnerabilities:**
- ❌ No authentication on admin panel
- ❌ No input sanitization (XSS possible)
- ❌ No CSRF protection
- ❌ No rate limiting

**Endpoints:**
- `http://localhost:5000/` - Homepage
- `http://localhost:5000/about` - About page
- `http://localhost:5000/admin` - Admin panel (vulnerable)
- `http://localhost:5000/api/content` - Content API

### 2. Detection Monitor (`detection_monitor.py`)

**Detection Methods:**

**File Integrity Monitoring:**
- Creates SHA-256 hashes of monitored files
- Detects any file modifications or deletions
- Compares current state to baseline

**Content Monitoring:**
- Fetches website content via API
- Compares to baseline content
- Detects keyword-based defacements

**Alert Levels:**
- 🚨 **CRITICAL**: File deleted, defacement keywords detected
- ⚠️ **HIGH**: File modified
- ⚡ **MEDIUM**: Content changed
- ℹ️ **LOW**: Minor changes

### 3. Attack Simulator (`attack_simulator.py`)

Simulates real-world attacks for testing:
- Homepage defacement
- XSS injection
- Phishing pages
- Malicious redirects
- Crypto mining scripts

## 📊 Monitoring Output

### Console Output Example:
```
[14:23:15] Check #1... ✓ No changes
[14:23:18] Check #2... ✓ No changes
[14:23:21] Check #3... ⚠️  CHANGES DETECTED!

🚨 CRITICAL ALERT
   Type: CONTENT_MODIFIED
   Details: Website content modified: homepage_title, homepage_content
   Changes: 2 detected
```

### Log Files:

**`logs/defacement_alerts.json`** - Machine-readable alerts:
```json
{
  "timestamp": "2024-10-12T14:23:21.123456",
  "type": "CONTENT_MODIFIED",
  "severity": "CRITICAL",
  "details": "Website content modified",
  "changes": {...}
}
```

**`logs/detection_log.txt`** - Human-readable log:
```
============================================================
[2024-10-12T14:23:21.123456] CRITICAL ALERT
Type: CONTENT_MODIFIED
Details: Website content has been modified
============================================================
```

## 🧪 Testing Scenarios

### Scenario 1: Simple Defacement Detection

1. Start server and monitor
2. Run attack simulator → choose option 1
3. Watch monitor detect changes immediately
4. Check logs for detailed information

### Scenario 2: Manual Attack via Browser

1. Start server and monitor
2. Open browser: `http://localhost:5000/admin`
3. Change content to: `<h1>HACKED</h1>`
4. Submit form
5. Monitor detects change within seconds

### Scenario 3: Generate Report

1. Run multiple attacks
2. Run detection monitor
3. Choose option 3 (Generate report)
4. View statistics and recent alerts

## 🔧 Configuration

### Changing Monitor Interval

Edit `src/detection_monitor.py`:
```python
CHECK_INTERVAL = 3  # Change to desired seconds
```

### Adding More Files to Monitor

Edit `src/detection_monitor.py` in `main()`:
```python
FILES_TO_MONITOR = [
    DATA_DIR / 'website_content.json',
    BASE_DIR / 'logs' / 'change_log.json',
    # Add more files here
]
```

### Changing Server Port

Edit `src/vulnerable_server.py`:
```python
app.run(
    host='127.0.0.1',
    port=5000,  # Change to desired port
    debug=True
)
```

Also update in `src/detection_monitor.py` and `src/attack_simulator.py`:
```python
WEBSITE_URL = 'http://localhost:5000'  # Update port
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to server"

**Solution:**
1. Ensure vulnerable server is running in Terminal 1
2. Check URL is correct: `http://localhost:5000`
3. Check firewall isn't blocking port 5000

### Issue: "No baseline found"

**Solution:**
1. Run detection monitor
2. Choose option 1 to create baseline
3. Then use option 2 for subsequent runs

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Virtual environment activation fails

**Windows PowerShell users:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\Activate.ps1
```

**Git Bash on Windows:**
```bash
source venv/Scripts/activate
```

### Issue: Port already in use

**Solution:**
```bash
# Find and kill process using port 5000

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

### Issue: Permission denied on file operations

**Solution:**
```bash
# Ensure directories exist and have proper permissions
chmod 755 data logs  # macOS/Linux only
```

## 📚 Learning Objectives

### What You'll Learn:

1. **Web Security Concepts:**
   - XSS (Cross-Site Scripting)
   - CSRF (Cross-Site Request Forgery)
   - Input validation importance
   - Authentication bypass

2. **Detection Techniques:**
   - File integrity monitoring (FIM)
   - Content hashing (SHA-256)
   - Baseline comparison
   - Real-time change detection

3. **Python Skills:**
   - Flask web framework
   - File I/O operations
   - HTTP requests
   - JSON data handling
   - Event-driven programming

4. **System Monitoring:**
   - Log management
   - Alert systems
   - Reporting and analysis

## 🔐 Security Best Practices Demonstrated

### What NOT to Do (as shown in vulnerable_server.py):
- ❌ No authentication checks
- ❌ Accepting unsanitized user input
- ❌ No CSRF tokens
- ❌ Running in debug mode in production
- ❌ Weak secret keys

### What TO Do (as shown in detection_monitor.py):
- ✅ Create baselines of known-good states
- ✅ Continuous monitoring
- ✅ Multiple detection methods
- ✅ Comprehensive logging
- ✅ Automated alerts
- ✅ Regular integrity checks

## 📈 Advanced Usage

### Custom Alert Actions

You can extend `detection_monitor.py` to add custom actions when defacement is detected:

```python
def log_alert(self, alert_type, severity, details, changes=None):
    # ... existing code ...
    
    # Add custom actions
    if severity == 'CRITICAL':
        self.send_email_alert(details)
        self.backup_current_state()
        self.rollback_to_baseline()
```

### Integration with External Services

Add email notifications, Slack alerts, or SMS:

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(self, details):
    msg = MIMEText(f"CRITICAL ALERT: {details}")
    msg['Subject'] = 'Website Defacement Detected'
    msg['From'] = 'monitor@example.com'
    msg['To'] = 'admin@example.com'
    
    # Send email (configure SMTP server)
```

### Automated Response

Implement automatic restoration:

```python
def auto_restore(self):
    """Automatically restore from baseline on critical alerts"""
    if self.baseline_file.exists():
        # Restore files from baseline
        for filepath, baseline_hash in self.baseline_hashes.items():
            # Restore logic here
            pass
```

## 📖 API Reference

### DetacementDetector Class

#### Methods:

**`__init__(website_url, files_to_monitor, check_interval)`**
- Initialize detector with target URL and files to monitor

**`create_baseline()`**
- Create initial baseline of file hashes and content

**`load_baseline()`**
- Load existing baseline from file
- Returns: `True` if successful, `False` otherwise

**`check_file_integrity()`**
- Check if monitored files have changed
- Returns: List of changed file paths

**`check_content_changes()`**
- Check if website content has changed
- Returns: List of changed content fields

**`monitor_continuous()`**
- Start continuous monitoring loop
- Runs until Ctrl+C

**`generate_report()`**
- Generate summary report of all detections

**`log_alert(alert_type, severity, details, changes)`**
- Log alert to files and console

### AttackSimulator Class

#### Methods:

**`check_server_status()`**
- Verify target server is running
- Returns: `True` if accessible, `False` otherwise

**`simulate_simple_defacement()`**
- Execute obvious homepage defacement

**`simulate_xss_injection()`**
- Inject XSS script into page

**`simulate_subtle_defacement()`**
- Make hard-to-detect changes

**`simulate_phishing_page()`**
- Replace page with credential theft form

**`restore_original_content()`**
- Restore website to original state

## 🧪 Testing Checklist

- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Server running on port 5000
- [ ] Baseline created successfully
- [ ] Monitor detecting simple defacements
- [ ] Monitor detecting subtle changes
- [ ] Logs being generated correctly
- [ ] Alerts showing proper severity levels
- [ ] Report generation working
- [ ] Attack simulator working
- [ ] Content restoration working

## 🤝 Contributing

This is an educational project. Suggestions for improvements:
- Additional attack types
- Better detection algorithms
- Machine learning integration
- Visual dashboard
- Database integration
- Docker containerization

## 📄 License

This project is for educational purposes only. Use responsibly and ethically.

## ⚠️ Legal Disclaimer

**IMPORTANT:**
- Only use on systems you own or have explicit permission to test
- Never use on production systems without authorization
- Unauthorized access to computer systems is illegal
- The authors are not responsible for misuse of this software
- This is for learning and research purposes only

## 🎓 Educational Resources

### Learn More About:

**Web Security:**
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Web Security Academy: https://portswigger.net/web-security

**Python Security:**
- Python Security Best Practices
- Secure Coding Guidelines

**File Integrity Monitoring:**
- NIST Guidelines on FIM
- Industry standard FIM tools (OSSEC, Tripwire)

## 📞 Support

If you encounter issues:
1. Check the Troubleshooting section
2. Verify all setup steps were followed
3. Ensure all files are in correct locations
4. Check terminal output for specific errors

## 🔄 Version History

**v1.0.0** - Initial Release
- Basic defacement detection
- File integrity monitoring
- Content change detection
- Attack simulator
- Cross-platform support

## 🎯 Future Enhancements

Potential additions:
- [ ] Web dashboard for monitoring
- [ ] Database backend for logs
- [ ] Machine learning anomaly detection
- [ ] Multi-site monitoring
- [ ] Webhook integrations
- [ ] Docker support
- [ ] Automated backup/restore
- [ ] Network traffic monitoring
- [ ] Browser extension for testing

## 📝 Notes

- **Performance**: Monitor checks run every 3 seconds by default. Adjust based on your needs.
- **Storage**: Log files grow over time. Implement log rotation for long-term use.
- **Security**: This project demonstrates vulnerabilities. Never deploy vulnerable_server.py publicly.
- **Testing**: Always test in isolated environments (localhost, VMs, containers).

---

**Made with ❤️ for Cybersecurity Education**

*Remember: With great power comes great responsibility. Use these tools ethically and legally.*
>>>>>>> 3418e75 (First Commit)
