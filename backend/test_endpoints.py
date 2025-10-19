#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script
Tests all 22 endpoints with various scenarios
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.project_id = None
        self.task_id = None
        self.test_results = []
        
    def log_test(self, endpoint: str, method: str, status_code: int, success: bool, message: str = ""):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "success": success,
            "message": message,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {endpoint} - {status_code} - {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        if self.token:
            default_headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=default_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=default_headers)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, headers=default_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints")
        
        # Test 1: Signup
        signup_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.make_request("POST", "/auth/signup", signup_data)
        if response and response.status_code == 200:
            self.user_data = response.json()
            self.log_test("/auth/signup", "POST", response.status_code, True, "User created successfully")
        else:
            self.log_test("/auth/signup", "POST", response.status_code if response else 0, False, "Signup failed")
        
        # Test 2: Login
        login_data = {
            "username": "testuser123",
            "password": "password123"
        }
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            login_response = response.json()
            self.token = login_response["data"]["token"]
            self.log_test("/auth/login", "POST", response.status_code, True, "Login successful")
        else:
            self.log_test("/auth/login", "POST", response.status_code if response else 0, False, "Login failed")
        
        # Test 3: Verify Token
        response = self.make_request("GET", "/auth/verify")
        if response and response.status_code == 200:
            self.log_test("/auth/verify", "GET", response.status_code, True, "Token verified")
        else:
            self.log_test("/auth/verify", "GET", response.status_code if response else 0, False, "Token verification failed")
        
        # Test 4: Logout
        response = self.make_request("POST", "/auth/logout")
        if response and response.status_code == 200:
            self.log_test("/auth/logout", "POST", response.status_code, True, "Logout successful")
        else:
            self.log_test("/auth/logout", "POST", response.status_code if response else 0, False, "Logout failed")
    
    def test_project_endpoints(self):
        """Test project endpoints"""
        print("\n📁 Testing Project Endpoints")
        
        # Re-login for project tests
        login_data = {"username": "testuser123", "password": "password123"}
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            self.token = response.json()["data"]["token"]
        
        # Test 1: Create Project
        project_data = {
            "name": "Test Project",
            "description": "A test project for API testing"
        }
        response = self.make_request("POST", "/projects", project_data)
        if response and response.status_code == 200:
            self.project_id = response.json()["data"]["id"]
            self.log_test("/projects", "POST", response.status_code, True, "Project created successfully")
        else:
            self.log_test("/projects", "POST", response.status_code if response else 0, False, "Project creation failed")
        
        # Test 2: Get All Projects
        response = self.make_request("GET", "/projects")
        if response and response.status_code == 200:
            self.log_test("/projects", "GET", response.status_code, True, "Projects retrieved successfully")
        else:
            self.log_test("/projects", "GET", response.status_code if response else 0, False, "Failed to retrieve projects")
        
        # Test 3: Get Project by ID
        if self.project_id:
            response = self.make_request("GET", f"/projects/{self.project_id}")
            if response and response.status_code == 200:
                self.log_test(f"/projects/{self.project_id}", "GET", response.status_code, True, "Project retrieved successfully")
            else:
                self.log_test(f"/projects/{self.project_id}", "GET", response.status_code if response else 0, False, "Failed to retrieve project")
        
        # Test 4: Update Project
        if self.project_id:
            update_data = {
                "name": "Updated Test Project",
                "description": "Updated description"
            }
            response = self.make_request("PUT", f"/projects/{self.project_id}", update_data)
            if response and response.status_code == 200:
                self.log_test(f"/projects/{self.project_id}", "PUT", response.status_code, True, "Project updated successfully")
            else:
                self.log_test(f"/projects/{self.project_id}", "PUT", response.status_code if response else 0, False, "Project update failed")
    
    def test_task_endpoints(self):
        """Test task endpoints"""
        print("\n📋 Testing Task Endpoints")
        
        if not self.project_id:
            print("Skipping task tests - no project ID available")
            return
        
        # Test 1: Create Task
        task_data = {
            "title": "Test Task",
            "description": "A test task for API testing",
            "priority": "high",
            "due_date": "2025-12-31T23:59:59Z"
        }
        response = self.make_request("POST", f"/projects/{self.project_id}/tasks", task_data)
        if response and response.status_code == 200:
            self.task_id = response.json()["data"]["id"]
            self.log_test(f"/projects/{self.project_id}/tasks", "POST", response.status_code, True, "Task created successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/tasks", "POST", response.status_code if response else 0, False, "Task creation failed")
        
        # Test 2: Get Project Tasks
        response = self.make_request("GET", f"/projects/{self.project_id}/tasks")
        if response and response.status_code == 200:
            self.log_test(f"/projects/{self.project_id}/tasks", "GET", response.status_code, True, "Tasks retrieved successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/tasks", "GET", response.status_code if response else 0, False, "Failed to retrieve tasks")
        
        # Test 3: Get Task by ID
        if self.task_id:
            response = self.make_request("GET", f"/projects/{self.project_id}/tasks/{self.task_id}")
            if response and response.status_code == 200:
                self.log_test(f"/projects/{self.project_id}/tasks/{self.task_id}", "GET", response.status_code, True, "Task retrieved successfully")
            else:
                self.log_test(f"/projects/{self.project_id}/tasks/{self.task_id}", "GET", response.status_code if response else 0, False, "Failed to retrieve task")
        
        # Test 4: Update Task
        if self.task_id:
            update_data = {
                "title": "Updated Test Task",
                "description": "Updated task description",
                "priority": "medium"
            }
            response = self.make_request("PUT", f"/projects/{self.project_id}/tasks/{self.task_id}", update_data)
            if response and response.status_code == 200:
                self.log_test(f"/projects/{self.project_id}/tasks/{self.task_id}", "PUT", response.status_code, True, "Task updated successfully")
            else:
                self.log_test(f"/projects/{self.project_id}/tasks/{self.task_id}", "PUT", response.status_code if response else 0, False, "Task update failed")
        
        # Test 5: Update Task Status
        if self.task_id:
            status_data = {"status": "in_progress"}
            response = self.make_request("PATCH", f"/projects/{self.project_id}/tasks/{self.task_id}/status", status_data)
            if response and response.status_code == 200:
                self.log_test(f"/projects/{self.project_id}/tasks/{self.task_id}/status", "PATCH", response.status_code, True, "Task status updated successfully")
            else:
                self.log_test(f"/projects/{self.project_id}/tasks/{self.task_id}/status", "PATCH", response.status_code if response else 0, False, "Task status update failed")
    
    def test_member_endpoints(self):
        """Test team member endpoints"""
        print("\n👥 Testing Team Member Endpoints")
        
        if not self.project_id:
            print("Skipping member tests - no project ID available")
            return
        
        # Test 1: Add Team Member (create another user first)
        member_data = {
            "username": "testmember123",
            "email": "member@example.com",
            "password": "password123"
        }
        response = self.make_request("POST", "/auth/signup", member_data)
        if response and response.status_code == 200:
            self.log_test("/auth/signup", "POST", response.status_code, True, "Member user created")
        
        # Add member to project
        add_member_data = {
            "username": "testmember123",
            "role": "developer"
        }
        response = self.make_request("POST", f"/projects/{self.project_id}/members", add_member_data)
        if response and response.status_code == 200:
            self.log_test(f"/projects/{self.project_id}/members", "POST", response.status_code, True, "Team member added successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/members", "POST", response.status_code if response else 0, False, "Failed to add team member")
        
        # Test 2: Get Team Members
        response = self.make_request("GET", f"/projects/{self.project_id}/members")
        if response and response.status_code == 200:
            self.log_test(f"/projects/{self.project_id}/members", "GET", response.status_code, True, "Team members retrieved successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/members", "GET", response.status_code if response else 0, False, "Failed to retrieve team members")
        
        # Test 3: Update Team Member Role
        update_role_data = {"role": "manager"}
        response = self.make_request("PUT", f"/projects/{self.project_id}/members/testmember123", update_role_data)
        if response and response.status_code == 200:
            self.log_test(f"/projects/{self.project_id}/members/testmember123", "PUT", response.status_code, True, "Team member role updated successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/members/testmember123", "PUT", response.status_code if response else 0, False, "Failed to update team member role")
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        print("\n📊 Testing Analytics Endpoints")
        
        if not self.project_id:
            print("Skipping analytics tests - no project ID available")
            return
        
        # Test 1: Get Project Analytics
        response = self.make_request("GET", f"/projects/{self.project_id}/analytics")
        if response and response.status_code == 200:
            self.log_test(f"/projects/{self.project_id}/analytics", "GET", response.status_code, True, "Project analytics retrieved successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/analytics", "GET", response.status_code if response else 0, False, "Failed to retrieve project analytics")
        
        # Test 2: Get Timeline Analytics
        response = self.make_request("GET", f"/projects/{self.project_id}/analytics/timeline")
        if response and response.status_code == 200:
            self.log_test(f"/projects/{self.project_id}/analytics/timeline", "GET", response.status_code, True, "Timeline analytics retrieved successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/analytics/timeline", "GET", response.status_code if response else 0, False, "Failed to retrieve timeline analytics")
        
        # Test 3: Get Member Analytics
        response = self.make_request("GET", f"/projects/{self.project_id}/analytics/member/testuser123")
        if response and response.status_code == 200:
            self.log_test(f"/projects/{self.project_id}/analytics/member/testuser123", "GET", response.status_code, True, "Member analytics retrieved successfully")
        else:
            self.log_test(f"/projects/{self.project_id}/analytics/member/testuser123", "GET", response.status_code if response else 0, False, "Failed to retrieve member analytics")
    
    def test_dashboard_endpoint(self):
        """Test dashboard endpoint"""
        print("\n🏠 Testing Dashboard Endpoint")
        
        # Test: Get Dashboard Summary
        response = self.make_request("GET", "/dashboard")
        if response and response.status_code == 200:
            self.log_test("/dashboard", "GET", response.status_code, True, "Dashboard data retrieved successfully")
        else:
            self.log_test("/dashboard", "GET", response.status_code if response else 0, False, "Failed to retrieve dashboard data")
    
    def test_error_cases(self):
        """Test error handling"""
        print("\n🚨 Testing Error Cases")
        
        # Test 1: Unauthorized request
        response = self.make_request("GET", "/projects")
        if response and response.status_code == 401:
            self.log_test("/projects", "GET", response.status_code, True, "Unauthorized request properly rejected")
        else:
            self.log_test("/projects", "GET", response.status_code if response else 0, False, "Unauthorized request not properly handled")
        
        # Test 2: Invalid project ID
        response = self.make_request("GET", "/projects/invalid-id")
        if response and response.status_code == 404:
            self.log_test("/projects/invalid-id", "GET", response.status_code, True, "Invalid project ID properly handled")
        else:
            self.log_test("/projects/invalid-id", "GET", response.status_code if response else 0, False, "Invalid project ID not properly handled")
        
        # Test 3: Invalid data
        invalid_data = {"invalid": "data"}
        response = self.make_request("POST", "/projects", invalid_data)
        if response and response.status_code == 400:
            self.log_test("/projects", "POST", response.status_code, True, "Invalid data properly rejected")
        else:
            self.log_test("/projects", "POST", response.status_code if response else 0, False, "Invalid data not properly handled")
    
    def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data")
        
        # Delete task
        if self.task_id and self.project_id:
            response = self.make_request("DELETE", f"/projects/{self.project_id}/tasks/{self.task_id}")
            if response and response.status_code == 200:
                print("✅ Test task deleted")
        
        # Delete project
        if self.project_id:
            response = self.make_request("DELETE", f"/projects/{self.project_id}")
            if response and response.status_code == 200:
                print("✅ Test project deleted")
        
        # Note: User cleanup would require admin endpoint or manual database cleanup
    
    def generate_report(self):
        """Generate test report"""
        print("\n📊 Test Report")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['method']} {result['endpoint']}: {result['message']}")
        
        # Save detailed report
        with open("test_report.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed report saved to test_report.json")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting API Endpoint Tests")
        print("=" * 50)
        
        try:
            self.test_auth_endpoints()
            self.test_project_endpoints()
            self.test_task_endpoints()
            self.test_member_endpoints()
            self.test_analytics_endpoints()
            self.test_dashboard_endpoint()
            self.test_error_cases()
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
        except Exception as e:
            print(f"\n💥 Test suite failed with error: {e}")
        finally:
            self.cleanup()
            self.generate_report()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Project Management API endpoints")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for the API")
    parser.add_argument("--cleanup-only", action="store_true", help="Only run cleanup")
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    
    if args.cleanup_only:
        tester.cleanup()
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()
