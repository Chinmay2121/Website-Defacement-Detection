"""
Enhanced Defacement Detection System with Dynamic Vulnerability Monitoring
Monitors all vulnerability types demonstrated in the dynamic homepage
NEW FEATURES:
- Pattern-based XSS detection
- Anomaly detection for content changes
- Real-time vulnerability tracking
- Enhanced dashboard with live stats
"""

import hashlib
import os
import time
import json
import re
from datetime import datetime
from pathlib import Path
import requests
from flask import Flask, render_template_string, jsonify
import threading

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ''
    class Style:
        BRIGHT = RESET_ALL = ''


class EnhancedDynamicDetector:
    """Enhanced detector with pattern-based vulnerability detection"""
    
    def __init__(self, website_url, files_to_monitor, check_interval=5):
        """Initialize detector"""
        self.website_url = website_url
        self.files_to_monitor = [Path(f) for f in files_to_monitor]
        self.check_interval = check_interval
        self.baseline_hashes = {}
        self.baseline_content = {}
        self.baseline_images = {}
        
        # XSS patterns to detect
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'onerror\s*=',
            r'onload\s*=',
            r'onclick\s*=',
            r'alert\s*\(',
            r'eval\s*\(',
            r'<iframe',
        ]
        
        # Defacement keywords
        self.defacement_keywords = [
            'hacked', 'pwned', 'owned', 'defaced', 'breach', 
            'security', 'exploit', 'rooted', 'compromised',
            'cracked', 'takeover', 'anonymous'
        ]
        
        # Setup paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.logs_dir = self.base_dir / 'logs'
        
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.baseline_file = self.data_dir / 'baseline.json'
        self.alerts_file = self.logs_dir / 'defacement_alerts.json'
        self.detection_log = self.logs_dir / 'detection_log.txt'
        self.status_file = self.data_dir / 'monitor_status.json'
        self.vuln_stats_file = self.data_dir / 'vulnerability_stats.json'
        
        # Statistics
        self.total_checks = 0
        self.total_detections = 0
        self.vulnerability_counts = {
            'XSS': 0,
            'File_Modified': 0,
            'Image_Changed': 0,
            'Content_Modified': 0,
            'Suspicious_Pattern': 0
        }
        self.is_monitoring = False
        self.current_risk_level = 'LOW'
        self.last_check_time = None
        
        self._update_status()
    
    def calculate_hash(self, filepath):
        """Calculate SHA-256 hash of a file"""
        filepath = Path(filepath)
        if not filepath.exists():
            return None
        
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for block in iter(lambda: f.read(4096), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except Exception as e:
            self._print_error(f"Error hashing {filepath}: {e}")
            return None
    
    def get_website_content(self):
        """Fetch current website content via API"""
        try:
            response = requests.get(
                f"{self.website_url}/api/content",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self._print_warning(f"Could not fetch website content: {e}")
            return None
    
    def get_website_images(self):
        """Fetch image hashes from website API"""
        try:
            response = requests.get(
                f"{self.website_url}/api/images",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {img['filename']: img['hash'] for img in data.get('images', [])}
            return {}
        except Exception as e:
            self._print_warning(f"Could not fetch image data: {e}")
            return {}
    
    def detect_xss_patterns(self, text):
        """Detect XSS patterns in text content"""
        detected_patterns = []
        text_lower = text.lower()
        
        for pattern in self.xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                detected_patterns.append(pattern)
        
        return detected_patterns
    
    def detect_defacement_keywords(self, text):
        """Detect defacement keywords in content"""
        detected_keywords = []
        text_lower = text.lower()
        
        for keyword in self.defacement_keywords:
            if keyword in text_lower:
                detected_keywords.append(keyword)
        
        return detected_keywords
    
    def create_baseline(self):
        """Create baseline hashes for files, content, and images"""
        self._print_header("CREATING ENHANCED BASELINE WITH PATTERN DETECTION")
        
        # Hash files
        for filepath in self.files_to_monitor:
            file_hash = self.calculate_hash(filepath)
            if file_hash:
                self.baseline_hashes[str(filepath)] = file_hash
                self._print_success(f"File baseline: {filepath.name}")
                self._print_info(f"  Hash: {file_hash[:16]}...")
        
        # Get website content baseline
        content = self.get_website_content()
        if content:
            self.baseline_content = content
            self._print_success("Content baseline created")
            self._print_info(f"  Title: {content.get('homepage_title', 'N/A')}")
            
            # Check for patterns in baseline
            for key, value in content.items():
                if isinstance(value, str):
                    xss = self.detect_xss_patterns(value)
                    if xss:
                        self._print_warning(f"  XSS patterns detected in {key}: {len(xss)}")
        
        # Get image baseline
        images = self.get_website_images()
        if images:
            self.baseline_images = images
            self._print_success(f"Image baseline created ({len(images)} images)")
            for filename, img_hash in images.items():
                self._print_info(f"  {filename}: {img_hash[:16]}...")
        
        # Save baseline
        baseline_data = {
            'timestamp': datetime.now().isoformat(),
            'file_hashes': self.baseline_hashes,
            'website_content': self.baseline_content,
            'image_hashes': self.baseline_images
        }
        
        try:
            with open(self.baseline_file, 'w', encoding='utf-8') as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)
            self._print_success(f"Baseline saved to {self.baseline_file.name}")
        except Exception as e:
            self._print_error(f"Error saving baseline: {e}")
        
        self._print_divider()
    
    def load_baseline(self):
        """Load existing baseline"""
        if not self.baseline_file.exists():
            return False
        
        try:
            with open(self.baseline_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.baseline_hashes = data.get('file_hashes', {})
                self.baseline_content = data.get('website_content', {})
                self.baseline_images = data.get('image_hashes', {})
                self._print_success(f"Baseline loaded from {self.baseline_file.name}")
                return True
        except Exception as e:
            self._print_error(f"Error loading baseline: {e}")
            return False
    
    def log_alert(self, alert_type, severity, details, changes=None, patterns=None):
        """Log defacement alerts with vulnerability categorization"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'severity': severity,
            'details': details,
            'changes': changes,
            'patterns': patterns
        }
        
        # Update vulnerability counts
        if alert_type == 'XSS_DETECTED':
            self.vulnerability_counts['XSS'] += 1
        elif alert_type == 'FILE_MODIFIED':
            self.vulnerability_counts['File_Modified'] += 1
        elif alert_type in ['IMAGE_MODIFIED', 'IMAGE_DELETED', 'IMAGE_ADDED']:
            self.vulnerability_counts['Image_Changed'] += 1
        elif alert_type == 'CONTENT_MODIFIED':
            self.vulnerability_counts['Content_Modified'] += 1
        elif alert_type == 'SUSPICIOUS_PATTERN':
            self.vulnerability_counts['Suspicious_Pattern'] += 1
        
        # Update risk level
        if severity == 'CRITICAL':
            self.current_risk_level = 'CRITICAL'
        elif severity == 'HIGH' and self.current_risk_level not in ['CRITICAL']:
            self.current_risk_level = 'HIGH'
        elif severity == 'MEDIUM' and self.current_risk_level not in ['CRITICAL', 'HIGH']:
            self.current_risk_level = 'MEDIUM'
        
        # Save to JSON
        try:
            with open(self.alerts_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert, ensure_ascii=False) + '\n')
        except Exception as e:
            self._print_error(f"Error saving alert: {e}")
        
        # Save to readable log
        try:
            with open(self.detection_log, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{alert['timestamp']}] {severity} ALERT\n")
                f.write(f"Type: {alert_type}\n")
                f.write(f"Details: {details}\n")
                if changes:
                    f.write("Changes detected:\n")
                    for key, value in changes.items():
                        f.write(f"  - {key}: {value}\n")
                if patterns:
                    f.write("Patterns detected:\n")
                    for pattern in patterns:
                        f.write(f"  - {pattern}\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            self._print_error(f"Error writing to log: {e}")
        
        # Console output
        severity_emoji = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': '⚡',
            'LOW': 'ℹ️'
        }
        
        color_map = {
            'CRITICAL': Fore.RED,
            'HIGH': Fore.YELLOW,
            'MEDIUM': Fore.CYAN,
            'LOW': Fore.WHITE
        }
        
        emoji = severity_emoji.get(severity, '◆')
        color = color_map.get(severity, '')
        
        print(f"\n{color}{emoji} {severity} ALERT{Style.RESET_ALL}")
        print(f"   Type: {alert_type}")
        print(f"   Details: {details}")
        if changes:
            print(f"   Changes: {len(changes)} detected")
        if patterns:
            print(f"   Malicious patterns: {len(patterns)} found")
        
        self._update_status()
        self._save_vulnerability_stats()
    
    def check_file_integrity(self):
        """Check if monitored files have been modified"""
        changes_detected = []
        
        for filepath, baseline_hash in self.baseline_hashes.items():
            current_hash = self.calculate_hash(filepath)
            
            if current_hash is None:
                self.log_alert(
                    'FILE_DELETED',
                    'CRITICAL',
                    f'File {filepath} has been deleted or is inaccessible'
                )
                changes_detected.append(filepath)
            elif current_hash != baseline_hash:
                self.log_alert(
                    'FILE_MODIFIED',
                    'HIGH',
                    f'File {filepath} has been modified',
                    changes={
                        'old_hash': baseline_hash[:16] + '...',
                        'new_hash': current_hash[:16] + '...'
                    }
                )
                changes_detected.append(filepath)
        
        return changes_detected
    
    def check_content_changes(self):
        """Check if website content has been modified with XSS detection"""
        current_content = self.get_website_content()
        if not current_content:
            return []
        
        changes = {}
        detected_xss = []
        detected_keywords = []
        
        for key in self.baseline_content:
            if key in ['last_modified', 'logo_hash']:
                continue
            
            baseline_value = self.baseline_content.get(key, '')
            current_value = current_content.get(key, '')
            
            if baseline_value != current_value:
                changes[key] = {
                    'old': (baseline_value[:100] + '...' 
                           if len(str(baseline_value)) > 100 
                           else baseline_value),
                    'new': (current_value[:100] + '...' 
                           if len(str(current_value)) > 100 
                           else current_value)
                }
                
                # Check for XSS patterns
                if isinstance(current_value, str):
                    xss_patterns = self.detect_xss_patterns(current_value)
                    if xss_patterns:
                        detected_xss.extend(xss_patterns)
                    
                    # Check for defacement keywords
                    keywords = self.detect_defacement_keywords(current_value)
                    if keywords:
                        detected_keywords.extend(keywords)
        
        # Log XSS detection separately
        if detected_xss:
            self.log_alert(
                'XSS_DETECTED',
                'CRITICAL',
                f'XSS patterns detected in website content',
                changes=changes,
                patterns=detected_xss
            )
        
        # Log suspicious keywords
        if detected_keywords:
            self.log_alert(
                'SUSPICIOUS_PATTERN',
                'HIGH',
                f'Defacement keywords detected: {", ".join(set(detected_keywords))}',
                changes=changes,
                patterns=detected_keywords
            )
        
        # Log content changes
        if changes and not detected_xss:
            severity = 'HIGH' if detected_keywords else 'MEDIUM'
            self.log_alert(
                'CONTENT_MODIFIED',
                severity,
                f'Website content modified: {", ".join(changes.keys())}',
                changes=changes
            )
        
        return list(changes.keys())
    
    def check_image_integrity(self):
        """Check if images have been modified or replaced"""
        current_images = self.get_website_images()
        changes_detected = []
        
        for filename, baseline_hash in self.baseline_images.items():
            current_hash = current_images.get(filename)
            
            if current_hash is None:
                self.log_alert(
                    'IMAGE_DELETED',
                    'HIGH',
                    f'Image {filename} has been deleted',
                    changes={'filename': filename}
                )
                changes_detected.append(filename)
            elif current_hash != baseline_hash:
                self.log_alert(
                    'IMAGE_MODIFIED',
                    'HIGH',
                    f'Image {filename} has been modified or replaced',
                    changes={
                        'filename': filename,
                        'old_hash': baseline_hash[:16] + '...',
                        'new_hash': current_hash[:16] + '...'
                    }
                )
                changes_detected.append(filename)
        
        for filename in current_images:
            if filename not in self.baseline_images:
                self.log_alert(
                    'IMAGE_ADDED',
                    'MEDIUM',
                    f'New image detected: {filename}',
                    changes={'filename': filename}
                )
                changes_detected.append(filename)
        
        return changes_detected
    
    def _update_status(self):
        """Update monitoring status file"""
        status = {
            'is_monitoring': self.is_monitoring,
            'total_checks': self.total_checks,
            'total_detections': self.total_detections,
            'current_risk_level': self.current_risk_level,
            'last_check_time': self.last_check_time,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2)
        except Exception:
            pass
    
    def _save_vulnerability_stats(self):
        """Save vulnerability statistics"""
        stats = {
            'vulnerability_counts': self.vulnerability_counts,
            'total_detections': self.total_detections,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.vuln_stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
        except Exception:
            pass
    
    def monitor_continuous(self):
        """Continuously monitor for changes"""
        self._print_header("ENHANCED DETECTION SYSTEM ACTIVE", char='🔒')
        print(f"Monitoring interval: {self.check_interval} seconds")
        print(f"Monitored files: {len(self.files_to_monitor)}")
        print(f"Monitored images: {len(self.baseline_images)}")
        print(f"Website: {self.website_url}")
        print(f"XSS patterns: {len(self.xss_patterns)}")
        print(f"Defacement keywords: {len(self.defacement_keywords)}")
        print(f"\n{Fore.CYAN}Press Ctrl+C to stop monitoring...{Style.RESET_ALL}\n")
        
        self.is_monitoring = True
        self._update_status()
        
        try:
            while True:
                self.total_checks += 1
                self.last_check_time = datetime.now().isoformat()
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] Check #{self.total_checks}...", end=' ')
                
                # Check files
                file_changes = self.check_file_integrity()
                
                # Check content with pattern detection
                content_changes = self.check_content_changes()
                
                # Check images
                image_changes = self.check_image_integrity()
                
                if file_changes or content_changes or image_changes:
                    self.total_detections += 1
                    print(f"{Fore.RED}⚠️ CHANGES DETECTED!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✓ No changes{Style.RESET_ALL}")
                    # Decay risk level
                    if self.total_checks % 10 == 0:
                        if self.current_risk_level == 'CRITICAL':
                            self.current_risk_level = 'HIGH'
                        elif self.current_risk_level == 'HIGH':
                            self.current_risk_level = 'MEDIUM'
                        elif self.current_risk_level == 'MEDIUM':
                            self.current_risk_level = 'LOW'
                
                self._update_status()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.is_monitoring = False
            self._update_status()
            self._print_monitoring_stopped()
    
    # Helper methods for formatted output
    def _print_header(self, text, char='='):
        """Print formatted header"""
        divider = char * 60
        print(f"\n{Fore.CYAN}{divider}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{divider}{Style.RESET_ALL}")
    
    def _print_divider(self):
        """Print divider line"""
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def _print_success(self, text):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    
    def _print_error(self, text):
        """Print error message"""
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
    
    def _print_warning(self, text):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠️ {text}{Style.RESET_ALL}")
    
    def _print_info(self, text):
        """Print info message"""
        print(f"{Fore.WHITE}{text}{Style.RESET_ALL}")
    
    def _print_monitoring_stopped(self):
        """Print monitoring stopped summary"""
        print(f"\n\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.RED}🛑 MONITORING STOPPED{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"Total checks performed: {self.total_checks}")
        print(f"Total detections: {self.total_detections}")
        print(f"Final risk level: {self.current_risk_level}")
        print(f"\n{Fore.YELLOW}Vulnerability Breakdown:{Style.RESET_ALL}")
        for vuln_type, count in self.vulnerability_counts.items():
            if count > 0:
                print(f"  {vuln_type}: {count}")
        print(f"\nAlert log: {self.alerts_file}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")


# Global detector instance
detector = None


def create_dashboard_app():
    """Create Flask app for enhanced monitoring dashboard"""
    app = Flask(__name__)
    
    ENHANCED_DASHBOARD = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Enhanced Detection Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
                text-align: center;
            }
            .header h1 {
                color: #1e3c72;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                transition: transform 0.3s;
            }
            .stat-card:hover { transform: translateY(-5px); }
            .stat-value {
                font-size: 3em;
                font-weight: bold;
                margin: 10px 0;
            }
            .stat-label {
                color: #666;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .risk-indicator {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                margin-bottom: 30px;
            }
            .risk-badge {
                display: inline-block;
                padding: 20px 50px;
                border-radius: 50px;
                font-size: 2em;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 2px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            .risk-LOW {
                background: #4caf50;
                color: white;
                box-shadow: 0 5px 20px rgba(76, 175, 80, 0.4);
            }
            .risk-MEDIUM {
                background: #ff9800;
                color: white;
                box-shadow: 0 5px 20px rgba(255, 152, 0, 0.4);
            }
            .risk-HIGH {
                background: #ff5722;
                color: white;
                box-shadow: 0 5px 20px rgba(255, 87, 34, 0.4);
            }
            .risk-CRITICAL {
                background: #f44336;
                color: white;
                box-shadow: 0 5px 20px rgba(244, 67, 54, 0.4);
                animation: critical-pulse 1s infinite;
            }
            @keyframes critical-pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.08); }
            }
            .vuln-breakdown {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 30px;
            }
            .vuln-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                margin: 10px 0;
                background: #f5f5f5;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .vuln-name {
                font-size: 1.2em;
                font-weight: bold;
                color: #333;
            }
            .vuln-count {
                font-size: 1.5em;
                font-weight: bold;
                color: #f44336;
            }
            .alerts-section {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .alert-item {
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #ff5722;
                background: #fff3f3;
                border-radius: 5px;
            }
            .status-badge {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
            }
            .status-active { background: #4caf50; color: white; }
            .status-inactive { background: #9e9e9e; color: white; }
            .refresh-notice {
                text-align: center;
                color: white;
                margin-top: 20px;
                font-size: 0.9em;
            }
        </style>
        <script>
            setTimeout(function() { location.reload(); }, 3000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Enhanced Detection Dashboard</h1>
                <p class="subtitle">Real-time Vulnerability Monitoring & Pattern Detection</p>
                <p style="margin-top: 15px;">
                    <span class="status-badge {{ 'status-active' if status.is_monitoring else 'status-inactive' }}">
                        {{ 'MONITORING ACTIVE' if status.is_monitoring else 'MONITORING STOPPED' }}
                    </span>
                </p>
            </div>
            
            <div class="risk-indicator">
                <h2 style="color: #666; margin-bottom: 20px;">Current Threat Level</h2>
                <div class="risk-badge risk-{{ status.current_risk_level }}">
                    {{ status.current_risk_level }}
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Checks</div>
                    <div class="stat-value" style="color: #2196f3;">{{ status.total_checks }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Detections</div>
                    <div class="stat-value" style="color: #f44336;">{{ status.total_detections }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Detection Rate</div>
                    <div class="stat-value" style="color: #ff9800;">
                        {{ '%.1f' | format((status.total_detections / status.total_checks * 100) if status.total_checks > 0 else 0) }}%
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Last Check</div>
                    <div class="stat-value" style="color: #4caf50; font-size: 1.2em;">
                        {{ status.last_check_time.split('T')[1][:8] if status.last_check_time else 'N/A' }}
                    </div>
                </div>
            </div>
            
            <div class="vuln-breakdown">
                <h2 style="color: #1e3c72; margin-bottom: 20px;">🔍 Vulnerability Breakdown</h2>
                {% for vuln_type, count in vuln_stats.items() %}
                <div class="vuln-item">
                    <div class="vuln-name">
                        {% if vuln_type == 'XSS' %}🔓 Cross-Site Scripting (XSS)
                        {% elif vuln_type == 'File_Modified' %}📄 File Modifications
                        {% elif vuln_type == 'Image_Changed' %}🖼️ Image Changes
                        {% elif vuln_type == 'Content_Modified' %}📝 Content Modifications
                        {% elif vuln_type == 'Suspicious_Pattern' %}⚠️ Suspicious Patterns
                        {% else %}{{ vuln_type }}
                        {% endif %}
                    </div>
                    <div class="vuln-count">{{ count }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="alerts-section">
                <h2 style="color: #1e3c72; margin-bottom: 20px;">🚨 Recent Alerts</h2>
                {% if recent_alerts %}
                    {% for alert in recent_alerts %}
                    <div class="alert-item">
                        <strong>{{ alert.severity }}</strong> - {{ alert.type }}
                        <div>{{ alert.details }}</div>
                        {% if alert.patterns %}
                        <div style="margin-top: 5px; color: #d32f2f;">
                            <strong>Patterns:</strong> {{ alert.patterns|join(', ') }}
                        </div>
                        {% endif %}
                        <div style="color: #999; margin-top: 5px; font-size: 0.9em;">{{ alert.timestamp }}</div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="color: #4caf50; text-align: center; padding: 20px;">
                        ✓ No alerts - System is secure
                    </p>
                {% endif %}
            </div>
            
            <div class="refresh-notice">
                🔄 Dashboard auto-refreshes every 3 seconds
            </div>
        </div>
    </body>
    </html>
    """
    
    @app.route('/')
    def dashboard():
        """Main dashboard view"""
        status_file = Path(__file__).parent.parent / 'data' / 'monitor_status.json'
        vuln_stats_file = Path(__file__).parent.parent / 'data' / 'vulnerability_stats.json'
        
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
        except:
            status = {
                'is_monitoring': False,
                'total_checks': 0,
                'total_detections': 0,
                'current_risk_level': 'LOW',
                'last_check_time': None
            }
        
        try:
            with open(vuln_stats_file, 'r') as f:
                vuln_data = json.load(f)
                vuln_stats = vuln_data.get('vulnerability_counts', {})
        except:
            vuln_stats = {
                'XSS': 0,
                'File_Modified': 0,
                'Image_Changed': 0,
                'Content_Modified': 0,
                'Suspicious_Pattern': 0
            }
        
        alerts_file = Path(__file__).parent.parent / 'logs' / 'defacement_alerts.json'
        recent_alerts = []
        try:
            with open(alerts_file, 'r') as f:
                for line in f:
                    if line.strip():
                        recent_alerts.append(json.loads(line))
            recent_alerts = recent_alerts[-10:]
            recent_alerts.reverse()
        except:
            pass
        
        return render_template_string(
            ENHANCED_DASHBOARD, 
            status=status, 
            recent_alerts=recent_alerts,
            vuln_stats=vuln_stats
        )
    
    @app.route('/api/status')
    def api_status():
        """API endpoint for status"""
        status_file = Path(__file__).parent.parent / 'data' / 'monitor_status.json'
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
            return jsonify(status)
        except:
            return jsonify({'error': 'Status not available'}), 404
    
    return app


def run_dashboard(port=5001):
    """Run dashboard in separate thread"""
    app = create_dashboard_app()
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


def main():
    """Main entry point"""
    global detector
    
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║  ENHANCED DYNAMIC DETECTION SYSTEM                         ║
║  Pattern-Based Vulnerability Monitoring                    ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    
    WEBSITE_URL = 'http://localhost:5000'
    FILES_TO_MONITOR = [
        DATA_DIR / 'website_content.json',
        BASE_DIR / 'logs' / 'change_log.json'
    ]
    CHECK_INTERVAL = 3
    
    detector = EnhancedDynamicDetector(WEBSITE_URL, FILES_TO_MONITOR, CHECK_INTERVAL)
    
    print(f"\n{Fore.CYAN}Detection Capabilities:{Style.RESET_ALL}")
    print(f"  ✓ XSS pattern detection ({len(detector.xss_patterns)} patterns)")
    print(f"  ✓ Defacement keyword detection ({len(detector.defacement_keywords)} keywords)")
    print(f"  ✓ File integrity monitoring")
    print(f"  ✓ Image hash verification")
    print(f"  ✓ Real-time vulnerability categorization")
    
    print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
    print("1. Create new baseline")
    print("2. Load existing baseline and start monitoring")
    print("3. Start monitoring with enhanced web dashboard")
    print("4. Check current status (one-time check)")
    
    try:
        choice = input(f"\n{Fore.YELLOW}Select option (1/2/3/4): {Style.RESET_ALL}")
    except KeyboardInterrupt:
        print("\n\nExiting...")
        return
    
    if choice == '1':
        detector.create_baseline()
        try:
            start_monitoring = input(
                f"\n{Fore.YELLOW}Start monitoring now? (yes/no): {Style.RESET_ALL}"
            )
            if start_monitoring.lower() in ['yes', 'y']:
                detector.monitor_continuous()
        except KeyboardInterrupt:
            print("\n\nExiting...")
    
    elif choice == '2':
        if detector.load_baseline():
            detector.monitor_continuous()
        else:
            detector._print_error("No baseline found. Please create one first (option 1)")
    
    elif choice == '3':
        if detector.load_baseline():
            print(f"\n{Fore.GREEN}Starting enhanced monitoring with web dashboard...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Dashboard URL: http://localhost:5001{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Open this URL in your browser to view real-time status{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}Features: Vulnerability breakdown, pattern detection, live alerts{Style.RESET_ALL}\n")
            
            dashboard_thread = threading.Thread(target=run_dashboard, args=(5001,), daemon=True)
            dashboard_thread.start()
            
            time.sleep(2)
            detector.monitor_continuous()
        else:
            detector._print_error("No baseline found. Please create one first (option 1)")
    
    elif choice == '4':
        if detector.load_baseline():
            detector._print_header("PERFORMING ENHANCED STATUS CHECK")
            
            print(f"\n{Fore.CYAN}Checking file integrity...{Style.RESET_ALL}")
            file_changes = detector.check_file_integrity()
            
            print(f"{Fore.CYAN}Checking content with pattern detection...{Style.RESET_ALL}")
            content_changes = detector.check_content_changes()
            
            print(f"{Fore.CYAN}Checking image integrity...{Style.RESET_ALL}")
            image_changes = detector.check_image_integrity()
            
            if not file_changes and not content_changes and not image_changes:
                print(f"\n{Fore.GREEN}✅ No changes detected - Website is clean{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}⚠️ Changes detected!{Style.RESET_ALL}")
                if file_changes:
                    print(f"   Files modified: {len(file_changes)}")
                if content_changes:
                    print(f"   Content fields changed: {len(content_changes)}")
                if image_changes:
                    print(f"   Images changed: {len(image_changes)}")
                
                print(f"\n{Fore.YELLOW}Vulnerability Breakdown:{Style.RESET_ALL}")
                for vuln_type, count in detector.vulnerability_counts.items():
                    if count > 0:
                        print(f"   {vuln_type}: {count}")
            
            detector._print_divider()
        else:
            detector._print_error("No baseline found. Please create one first (option 1)")
    
    else:
        detector._print_error("Invalid choice")


if __name__ == '__main__':
    main()