import requests
import sys
import json
from datetime import datetime

class BeeHiveAPITester:
    def __init__(self, base_url="https://webvital-track.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.admin_user = None
        self.subadmin_user = None
        self.website_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_setup_status(self):
        """Test setup status endpoint"""
        success, response = self.run_test(
            "Check Setup Status",
            "GET",
            "setup/status",
            200
        )
        return success, response

    def test_initialize_setup(self):
        """Test setup initialization"""
        admin_data = {
            "username": f"admin_{datetime.now().strftime('%H%M%S')}",
            "email": f"admin_{datetime.now().strftime('%H%M%S')}@beehive.com",
            "password": "AdminPass123!",
            "role": "admin"
        }
        
        success, response = self.run_test(
            "Initialize Setup",
            "POST",
            "setup/initialize",
            200,
            data=admin_data
        )
        
        if success:
            self.admin_user = admin_data
        
        return success, response

    def test_login(self, username, password, totp_code=None):
        """Test login endpoint"""
        login_data = {
            "username": username,
            "password": password
        }
        if totp_code:
            login_data["totp_code"] = totp_code

        success, response = self.run_test(
            f"Login - {username}",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True, response
        
        return success, response

    def test_create_subadmin(self):
        """Test creating a sub-admin user"""
        subadmin_data = {
            "username": f"subadmin_{datetime.now().strftime('%H%M%S')}",
            "email": f"subadmin_{datetime.now().strftime('%H%M%S')}@beehive.com",
            "password": "SubAdminPass123!",
            "role": "subadmin"
        }
        
        success, response = self.run_test(
            "Create Sub-Admin",
            "POST",
            "auth/register",
            200,
            data=subadmin_data
        )
        
        if success:
            self.subadmin_user = subadmin_data
        
        return success, response

    def test_get_users(self):
        """Test getting users list"""
        return self.run_test(
            "Get Users List",
            "GET",
            "users",
            200
        )

    def test_create_website(self):
        """Test creating a website"""
        website_data = {
            "name": "Test Website",
            "url": "https://httpbin.org/status/200"
        }
        
        success, response = self.run_test(
            "Create Website",
            "POST",
            "websites",
            200,
            data=website_data
        )
        
        if success and 'id' in response:
            self.website_id = response['id']
        
        return success, response

    def test_get_websites(self):
        """Test getting websites list"""
        return self.run_test(
            "Get Websites List",
            "GET",
            "websites",
            200
        )

    def test_check_website(self):
        """Test manual website check"""
        if not self.website_id:
            self.log_test("Check Website", False, "No website ID available")
            return False, {}
        
        return self.run_test(
            "Check Website",
            "POST",
            f"websites/{self.website_id}/check",
            200
        )

    def test_get_monitoring_data(self):
        """Test getting monitoring data"""
        if not self.website_id:
            self.log_test("Get Monitoring Data", False, "No website ID available")
            return False, {}
        
        return self.run_test(
            "Get Monitoring Data",
            "GET",
            f"monitoring/{self.website_id}",
            200
        )

    def test_weekly_stats(self):
        """Test weekly stats endpoint"""
        return self.run_test(
            "Get Weekly Stats",
            "GET",
            "stats/weekly",
            200
        )

    def test_change_password(self):
        """Test password change"""
        password_data = {
            "old_password": self.admin_user["password"],
            "new_password": "NewAdminPass123!"
        }
        
        success, response = self.run_test(
            "Change Password",
            "POST",
            "auth/change-password",
            200,
            data=password_data
        )
        
        if success:
            self.admin_user["password"] = password_data["new_password"]
        
        return success, response

    def test_2fa_setup(self):
        """Test 2FA setup"""
        return self.run_test(
            "Setup 2FA",
            "POST",
            "auth/2fa/setup",
            200
        )

    def test_delete_website(self):
        """Test deleting a website"""
        if not self.website_id:
            self.log_test("Delete Website", False, "No website ID available")
            return False, {}
        
        return self.run_test(
            "Delete Website",
            "DELETE",
            f"websites/{self.website_id}",
            200
        )

    def test_delete_subadmin(self):
        """Test deleting a sub-admin"""
        # First get users to find the subadmin ID
        success, users_response = self.test_get_users()
        if not success or not users_response:
            self.log_test("Delete Sub-Admin", False, "Could not get users list")
            return False, {}
        
        subadmin_id = None
        for user in users_response:
            if user.get('username') == self.subadmin_user['username']:
                subadmin_id = user['id']
                break
        
        if not subadmin_id:
            self.log_test("Delete Sub-Admin", False, "Sub-admin not found")
            return False, {}
        
        return self.run_test(
            "Delete Sub-Admin",
            "DELETE",
            f"users/{subadmin_id}",
            200
        )

    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🐝 Starting BeeHive API Tests...")
        print("=" * 50)
        
        # Test setup flow
        print("\n📋 Testing Setup Flow...")
        setup_success, setup_response = self.test_setup_status()
        
        if setup_success and not setup_response.get('setup_complete', True):
            self.test_initialize_setup()
        
        # Test authentication
        print("\n🔐 Testing Authentication...")
        if self.admin_user:
            login_success, login_response = self.test_login(
                self.admin_user["username"], 
                self.admin_user["password"]
            )
            
            if not login_success:
                print("❌ Cannot continue without valid login")
                return self.get_summary()
        
        # Test user management
        print("\n👥 Testing User Management...")
        self.test_create_subadmin()
        self.test_get_users()
        
        # Test website management
        print("\n🌐 Testing Website Management...")
        self.test_create_website()
        self.test_get_websites()
        self.test_check_website()
        
        # Wait a bit for monitoring data
        print("\n⏳ Waiting for monitoring data...")
        import time
        time.sleep(3)
        
        self.test_get_monitoring_data()
        
        # Test stats and settings
        print("\n📊 Testing Stats & Settings...")
        self.test_weekly_stats()
        self.test_change_password()
        self.test_2fa_setup()
        
        # Cleanup tests
        print("\n🧹 Testing Cleanup...")
        self.test_delete_website()
        self.test_delete_subadmin()
        
        return self.get_summary()

    def get_summary(self):
        """Get test summary"""
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check details above.")
            failed_tests = [r for r in self.test_results if not r['success']]
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return False

def main():
    """Main test function"""
    tester = BeeHiveAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())