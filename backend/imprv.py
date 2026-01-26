"""
COMPREHENSIVE ADMIN ENDPOINTS TESTER
Tests all admin endpoints and saves detailed results
"""
import requests
import json
import time
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

@dataclass
class AdminTestResult:
    """Admin test result container"""
    endpoint: str
    method: str
    success: bool
    status_code: int
    response_time: float
    error: Optional[str] = None
    details: Optional[Dict] = None
    admin_required: bool = False

class AdminTester:
    """Comprehensive Admin API tester"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.admin_user = None
        self.test_results = []
        self.output_file = "admin_output.txt"
        
        # Admin test credentials (you'll need to create this admin user first)
        self.admin_email = "admin@fsociety.test"
        self.admin_password = "AdminPass123!"
        self.admin_username = "admin_tester"
        
        # Initialize output file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("FSOCIETY ADMIN ENDPOINTS TEST REPORT\n")
            f.write("="*60 + "\n\n")
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        
        # Write to output file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def print_header(self, text: str):
        """Print formatted header"""
        header = f"\n{'='*60}\n{text}\n{'='*60}"
        print(f"{Fore.CYAN}{header}{Style.RESET_ALL}")
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(header + '\n')
    
    def print_result(self, result: AdminTestResult):
        """Print test result with colors"""
        if result.success:
            status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}"
        else:
            if result.admin_required:
                status = f"{Fore.YELLOW}⚠ EXPECTED FAIL (Admin){Style.RESET_ALL}"
            else:
                status = f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
        
        result_line = f"{status} {result.method:6} {result.endpoint:40} {result.status_code:4} {result.response_time:.2f}s"
        print(result_line)
        
        # Write to file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(result_line + '\n')
        
        if result.error:
            error_msg = f"   Error: {result.error}"
            print(f"{Fore.YELLOW}{error_msg}{Style.RESET_ALL}")
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(error_msg + '\n')
        
        if result.details and not result.success:
            details = f"   Details: {json.dumps(result.details, indent=2)}"
            print(f"{Fore.BLUE}{details}{Style.RESET_ALL}")
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(details + '\n')
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> AdminTestResult:
        """Make HTTP request and measure time"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if token exists
        if self.access_token and 'headers' not in kwargs:
            kwargs['headers'] = {'Authorization': f'Bearer {self.access_token}'}
        
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response_time = time.time() - start_time
            
            try:
                response_data = response.json()
            except:
                response_data = {'raw_response': response.text}
            
            success = 200 <= response.status_code < 300
            
            return AdminTestResult(
                endpoint=endpoint,
                method=method,
                success=success,
                status_code=response.status_code,
                response_time=response_time,
                error=None if success else f"HTTP {response.status_code}",
                details=response_data if isinstance(response_data, dict) else {"response": response_data}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return AdminTestResult(
                endpoint=endpoint,
                method=method,
                success=False,
                status_code=0,
                response_time=response_time,
                error=str(e)
            )
    
    def setup_admin_user(self):
        """Setup admin user for testing"""
        self.print_header("🛠️  SETTING UP ADMIN USER")
        
        # First, try to login as existing admin
        login_data = {"email": self.admin_email, "password": self.admin_password}
        result = self.make_request("POST", "/api/auth/login", json=login_data)
        
        if result.success:
            self.access_token = result.details.get('access_token')
            self.refresh_token = result.details.get('refresh_token')
            
            # Verify admin role
            user_result = self.make_request("GET", "/api/auth/me")
            if user_result.success:
                self.admin_user = user_result.details
                if self.admin_user.get('role') == 'admin':
                    self.log(f"✅ Successfully logged in as admin: {self.admin_user.get('email')}")
                else:
                    self.log(f"⚠️  User is not admin, but proceeding with tests anyway")
            return
        
        # If login fails, create new admin user (if you have permissions)
        self.log("Admin login failed. Attempting to create regular user first...")
        
        # Create regular test user
        timestamp = int(time.time())
        regular_email = f"regular_{timestamp}@fsociety.test"
        regular_password = "RegularPass123!"
        
        signup_data = {
            "email": regular_email,
            "password": regular_password,
            "username": f"regular_{timestamp}",
            "role": "user"
        }
        
        signup_result = self.make_request("POST", "/api/auth/signup", json=signup_data)
        
        if signup_result.success:
            # Login as regular user
            regular_login = {"email": regular_email, "password": regular_password}
            login_result = self.make_request("POST", "/api/auth/login", json=regular_login)
            
            if login_result.success:
                self.access_token = login_result.details.get('access_token')
                self.log(f"✅ Created regular user for testing: {regular_email}")
                self.log(f"⚠️  Note: Regular user cannot access admin endpoints. Admin tests will fail as expected.")
            else:
                self.log(f"❌ Failed to login as regular user")
        else:
            self.log(f"❌ Failed to create test user. Tests may fail.")
    
    def test_admin_auth_endpoints(self):
        """Test admin authentication and basic endpoints"""
        self.print_header("🔐 ADMIN AUTHENTICATION TESTS")
        
        # 1. Test admin-only endpoint without auth
        original_token = self.access_token
        self.access_token = None
        result = self.make_request("GET", "/api/admin/users?limit=1")
        result.admin_required = True
        self.test_results.append(result)
        self.print_result(result)
        self.access_token = original_token
        
        # 2. Test admin-only endpoint with regular user (if not admin)
        if self.admin_user and self.admin_user.get('role') != 'admin':
            result = self.make_request("GET", "/api/admin/users?limit=1")
            result.admin_required = True
            self.test_results.append(result)
            self.print_result(result)
    
    def test_user_management_admin(self):
        """Test admin user management endpoints"""
        self.print_header("👥 ADMIN USER MANAGEMENT")
        
        # 1. Get all users
        result = self.make_request("GET", "/api/admin/users?limit=5")
        self.test_results.append(result)
        self.print_result(result)
        
        # 2. Get users with filters
        result = self.make_request("GET", "/api/admin/users?limit=3&role=user&active_only=true")
        self.test_results.append(result)
        self.print_result(result)
        
        # 3. Get specific user (if we have user ID from previous calls)
        if result.success and result.details and result.details.get('users'):
            user_id = result.details['users'][0].get('id')
            if user_id:
                result = self.make_request("GET", f"/api/admin/users/{user_id}")
                self.test_results.append(result)
                self.print_result(result)
        
        # 4. Update user (if we have user ID)
        if 'user_id' in locals() and user_id:
            update_data = {
                "username": f"updated_admin_test_{int(time.time())}",
                "is_active": True
            }
            result = self.make_request("PUT", f"/api/admin/users/{user_id}", json=update_data)
            self.test_results.append(result)
            self.print_result(result)
        
        # 5. Test invalid user ID
        result = self.make_request("GET", "/api/admin/users/invalid-user-id-123")
        self.test_results.append(result)
        self.print_result(result)
        
        # Note: Delete user test is skipped for safety
    
    def test_platform_statistics(self):
        """Test platform statistics endpoints"""
        self.print_header("📊 PLATFORM STATISTICS")
        
        # 1. Get platform stats
        result = self.make_request("GET", "/api/admin/stats")
        self.test_results.append(result)
        self.print_result(result)
        
        # 2. Get all activities
        result = self.make_request("GET", "/api/admin/activities?limit=10")
        self.test_results.append(result)
        self.print_result(result)
        
        # 3. Get filtered activities
        result = self.make_request("GET", "/api/admin/activities?action=login&limit=5")
        self.test_results.append(result)
        self.print_result(result)
        
        # 4. Get activities with date range
        result = self.make_request("GET", "/api/admin/activities?date_from=2024-01-01&limit=3")
        self.test_results.append(result)
        self.print_result(result)
    
    def test_scan_management_admin(self):
        """Test admin scan management endpoints"""
        self.print_header("🔍 ADMIN SCAN MANAGEMENT")
        
        # 1. Get all scans via admin endpoint
        result = self.make_request("GET", "/api/admin/scans?limit=5")
        self.test_results.append(result)
        self.print_result(result)
        
        # 2. Get all scans via scanning module admin endpoint
        result = self.make_request("GET", "/api/scans/admin/all?limit=3")
        self.test_results.append(result)
        self.print_result(result)
        
        # 3. Get specific scan (if we have scan IDs)
        if result.success and result.details and result.details.get('scans'):
            scans = result.details['scans']
            if scans:
                scan_id = scans[0].get('id')
                result = self.make_request("GET", f"/api/scans/{scan_id}")
                self.test_results.append(result)
                self.print_result(result)
                
                # 4. Test admin delete scan (commented for safety)
                # result = self.make_request("DELETE", f"/api/scans/admin/{scan_id}")
                # self.test_results.append(result)
                # self.print_result(result)
        
        # 5. Test invalid scan ID
        result = self.make_request("DELETE", "/api/scans/admin/invalid-scan-id-123")
        self.test_results.append(result)
        self.print_result(result)
    
    def test_security_admin_endpoints(self):
        """Test admin security scanning endpoints"""
        self.print_header("🛡️ ADMIN SECURITY ENDPOINTS")
        
        # 1. Get cache statistics
        result = self.make_request("GET", "/api/security/cache/stats")
        self.test_results.append(result)
        self.print_result(result)
        
        # 2. Get cache entries
        result = self.make_request("GET", "/api/security/cache/entries?limit=5")
        self.test_results.append(result)
        self.print_result(result)
        
        # 3. Clear cache (specific type)
        result = self.make_request("POST", "/api/security/cache/clear?cache_type=ssl")
        self.test_results.append(result)
        self.print_result(result)
        
        # 4. Clear all cache
        result = self.make_request("POST", "/api/security/cache/clear")
        self.test_results.append(result)
        self.print_result(result)
    
    def test_file_analysis_admin(self):
        """Test admin file analysis endpoints"""
        self.print_header("📁 ADMIN FILE ANALYSIS")
        
        # 1. Get malware database info
        result = self.make_request("GET", "/api/files/malware/database")
        self.test_results.append(result)
        self.print_result(result)
        
        # 2. Update malware database
        test_hash = hashlib.sha256(b"test_malware_sample").hexdigest()
        update_data = [{
            "sha256": test_hash,
            "md5": hashlib.md5(b"test_malware_sample").hexdigest(),
            "sha1": hashlib.sha1(b"test_malware_sample").hexdigest(),
            "names": ["Test Malware Sample"],
            "tags": ["test", "sample"],
            "file_type": "executable",
            "file_size": 1024,
            "first_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "detections": 1
        }]
        
        result = self.make_request("POST", "/api/files/malware/database/update", json=update_data)
        self.test_results.append(result)
        self.print_result(result)
        
        # 3. Test the updated hash
        if result.success:
            hash_data = {"hash": test_hash, "hash_type": "sha256"}
            result = self.make_request("POST", "/api/files/hash/check", json=hash_data)
            self.test_results.append(result)
            self.print_result(result)
    
    def test_system_endpoints(self):
        """Test system and health endpoints"""
        self.print_header("⚙️ SYSTEM ENDPOINTS")
        
        # 1. Detailed health check
        result = self.make_request("GET", "/api/security/health/detailed")
        self.test_results.append(result)
        self.print_result(result)
        
        # 2. Status endpoint
        result = self.make_request("GET", "/status")
        self.test_results.append(result)
        self.print_result(result)
        
        # 3. Health endpoint
        result = self.make_request("GET", "/health")
        self.test_results.append(result)
        self.print_result(result)
        
        # 4. Root endpoint
        result = self.make_request("GET", "/")
        self.test_results.append(result)
        self.print_result(result)
    
    def run_all_admin_tests(self):
        """Run all admin tests"""
        self.print_header("🚀 STARTING ADMIN ENDPOINTS TEST SUITE")
        self.log(f"Base URL: {self.base_url}")
        self.log(f"Admin User: {self.admin_email}")
        self.log(f"Output File: {self.output_file}")
        
        try:
            # Setup admin user
            self.setup_admin_user()
            
            # Run all test categories
            self.test_admin_auth_endpoints()
            self.test_user_management_admin()
            self.test_platform_statistics()
            self.test_scan_management_admin()
            self.test_security_admin_endpoints()
            self.test_file_analysis_admin()
            self.test_system_endpoints()
            
            # Generate summary
            self.generate_summary()
            
        except KeyboardInterrupt:
            self.log("\n⚠️  Testing interrupted by user", "WARNING")
        except Exception as e:
            self.log(f"\n❌ Testing failed with error: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        self.print_header("📊 ADMIN TESTS SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        expected_fails = sum(1 for r in self.test_results if not r.success and r.admin_required)
        unexpected_fails = total_tests - passed_tests - expected_fails
        
        # Calculate stats
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        avg_response_time = sum(r.response_time for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        # Summary table
        summary_data = [
            ("Total Tests", f"{total_tests}"),
            ("✅ Passed", f"{passed_tests}"),
            ("⚠️ Expected Fails", f"{expected_fails}"),
            ("❌ Unexpected Fails", f"{unexpected_fails}"),
            ("Success Rate", f"{success_rate:.1f}%"),
            ("Avg Response Time", f"{avg_response_time:.2f}s")
        ]
        
        for label, value in summary_data:
            line = f"{label:20} {value}"
            print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        
        # Detailed breakdown
        self.print_header("📈 ENDPOINT BREAKDOWN")
        
        # Group by endpoint category
        categories = {
            'auth': [],
            'users': [],
            'stats': [],
            'scans': [],
            'security': [],
            'files': [],
            'system': []
        }
        
        for result in self.test_results:
            endpoint = result.endpoint
            if '/api/auth' in endpoint:
                categories['auth'].append(result)
            elif '/api/admin/users' in endpoint:
                categories['users'].append(result)
            elif '/api/admin/stats' in endpoint or '/api/admin/activities' in endpoint:
                categories['stats'].append(result)
            elif '/api/admin/scans' in endpoint or '/scans/admin' in endpoint:
                categories['scans'].append(result)
            elif '/api/security/cache' in endpoint:
                categories['security'].append(result)
            elif '/api/files/malware' in endpoint:
                categories['files'].append(result)
            elif '/health' in endpoint or '/status' in endpoint or '/' == endpoint:
                categories['system'].append(result)
        
        for category, results in categories.items():
            if results:
                total = len(results)
                passed = sum(1 for r in results if r.success)
                rate = (passed / total * 100) if total > 0 else 0
                
                status = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
                line = f"  {status} {category.upper():10} {passed:2}/{total:2} ({rate:5.1f}%)"
                print(line)
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(line + '\n')
        
        # List unexpected failures
        if unexpected_fails > 0:
            self.print_header("🔴 UNEXPECTED FAILURES")
            for result in self.test_results:
                if not result.success and not result.admin_required:
                    line = f"❌ {result.method} {result.endpoint}: {result.error}"
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                    with open(self.output_file, 'a', encoding='utf-8') as f:
                        f.write(line + '\n')
        
        # List expected failures (admin access required)
        if expected_fails > 0:
            self.print_header("⚠️ EXPECTED FAILURES (Admin Access Required)")
            for result in self.test_results:
                if not result.success and result.admin_required:
                    line = f"⚠️ {result.method} {result.endpoint}: Admin access required"
                    print(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
                    with open(self.output_file, 'a', encoding='utf-8') as f:
                        f.write(line + '\n')
        
        # Recommendations
        self.print_header("💡 RECOMMENDATIONS")
        
        recommendations = []
        
        if success_rate >= 90:
            recommendations.append("✅ Excellent! Admin endpoints are working correctly.")
        elif success_rate >= 70:
            recommendations.append("⚠️ Good, but some admin endpoints need attention.")
        else:
            recommendations.append("❌ Needs improvement. Review failed endpoints.")
        
        if unexpected_fails > 0:
            recommendations.append(f"❌ Fix {unexpected_fails} unexpected failure(s).")
        
        if self.admin_user and self.admin_user.get('role') != 'admin':
            recommendations.append("⚠️ Current user is not admin. Admin tests will fail.")
            recommendations.append("💡 Create an admin user with: role='admin' in signup")
        
        if avg_response_time > 2.0:
            recommendations.append(f"⚠️ High response time ({avg_response_time:.2f}s). Consider optimization.")
        
        for rec in recommendations:
            print(f"  {rec}")
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"  {rec}\n")
        
        # Final verdict
        self.print_header("🎯 FINAL VERDICT")
        
        if success_rate >= 90 and unexpected_fails == 0:
            verdict = "🎉 EXCELLENT! Admin endpoints are production-ready."
            color = Fore.GREEN
        elif success_rate >= 70 and unexpected_fails <= 2:
            verdict = "👍 GOOD! Admin endpoints are functional."
            color = Fore.YELLOW
        elif success_rate >= 50:
            verdict = "⚠️ FAIR. Admin endpoints work but need fixes."
            color = Fore.YELLOW
        else:
            verdict = "🔴 POOR. Admin endpoints need major fixes."
            color = Fore.RED
        
        print(f"{color}{verdict}{Style.RESET_ALL}")
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(verdict + '\n')
        
        # Save JSON results
        json_output = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'base_url': self.base_url,
            'admin_user': self.admin_email if self.admin_user else None,
            'is_admin': self.admin_user.get('role') == 'admin' if self.admin_user else False,
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'expected_fails': expected_fails,
                'unexpected_fails': unexpected_fails,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time
            },
            'results': [
                {
                    'endpoint': r.endpoint,
                    'method': r.method,
                    'success': r.success,
                    'status_code': r.status_code,
                    'response_time': r.response_time,
                    'error': r.error,
                    'admin_required': r.admin_required,
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                }
                for r in self.test_results
            ]
        }
        
        with open('admin_results.json', 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2)
        
        self.log(f"\n📁 Detailed results saved to: admin_results.json")
        self.log(f"📁 Log file: {self.output_file}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fsociety Admin Endpoints Tester')
    parser.add_argument('--url', default='http://localhost:8000', help='API base URL')
    parser.add_argument('--admin-email', default='admin@fsociety.test', help='Admin email')
    parser.add_argument('--admin-password', default='AdminPass123!', help='Admin password')
    parser.add_argument('--create-admin', action='store_true', help='Create admin user if needed')
    
    args = parser.parse_args()
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║           FSOCIETY ADMIN ENDPOINTS TESTER               ║
    ║                  Version 1.0.0                          ║
    ║     Testing ALL admin endpoints with detailed reporting ║
    ╚══════════════════════════════════════════════════════════╝
    
    Testing against: {args.url}
    Admin Email: {args.admin_email}
    
    Results will be saved to: admin_output.txt and admin_results.json
    
    Press Ctrl+C to stop testing at any time.
    """)
    
    tester = AdminTester(base_url=args.url)
    tester.admin_email = args.admin_email
    tester.admin_password = args.admin_password
    
    try:
        tester.run_all_admin_tests()
        
        # Show where results are saved
        print(f"\n{'='*60}")
        print(f"📊 Admin tests completed!")
        print(f"📁 Log file: admin_output.txt")
        print(f"📁 JSON results: admin_results.json")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Fatal error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()