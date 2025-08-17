#!/usr/bin/env python3
"""
Demo script to showcase the complete user authentication system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.auth import AuthenticationManager

def demo_authentication_system():
    """Demonstrate the complete authentication system"""
    auth = AuthenticationManager()
    
    print("🌟 Kannada PDF Toolkit - User Authentication System Demo")
    print("=" * 60)
    
    # Demo user registration
    print("\n📝 DEMO: User Registration")
    print("-" * 40)
    
    demo_users = [
        {
            "email": "rajesh.kumar@karnataka.gov.in",
            "password": "secure123",
            "name": "ರಾಜೇಶ್ ಕುಮಾರ್",
            "employee_id": "KGV101",
            "department": "ಕಲೆಕ್ಟರ್ ಕಚೇರಿ",
            "designation": "ಸಹಾಯಕ ಕಲೆಕ್ಟರ್"
        },
        {
            "email": "priya.sharma@example.com",
            "password": "mypassword456",
            "name": "ಪ್ರಿಯಾ ಶರ್ಮಾ",
            "department": "ಸಾಮಾನ್ಯ ಬಳಕೆದಾರ"
        }
    ]
    
    registered_users = []
    
    for i, user in enumerate(demo_users, 1):
        print(f"\n{i}. Registering user: {user['name']}")
        print(f"   Email: {user['email']}")
        
        success, message = auth.register_user(**user)
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"   Message: {message}")
        
        if success:
            registered_users.append(user)
    
    # Demo login functionality
    print("\n🔐 DEMO: Login Functionality")
    print("-" * 40)
    
    for i, user in enumerate(registered_users, 1):
        print(f"\n{i}. Testing login for: {user['name']}")
        
        # Test email login
        print("   Testing email login...")
        success, user_info = auth.authenticate_user_by_email(user['email'], user['password'])
        print(f"   Email login: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success and user_info:
            print(f"   Welcome: {user_info['name']}")
            print(f"   Department: {user_info['department']}")
            
            # Create session
            username = None
            users = auth.load_users()
            for uname, udata in users.items():
                if udata.get('email', '').lower() == user['email'].lower():
                    username = uname
                    break
            
            if username:
                session_token = auth.create_session(username)
                print(f"   Session created: {session_token[:16]}...")
                
                # Validate session
                valid, session_user = auth.validate_session(session_token)
                print(f"   Session validation: {'✅ VALID' if valid else '❌ INVALID'}")
                
                # Logout
                logout_success = auth.logout_session(session_token)
                print(f"   Logout: {'✅ SUCCESS' if logout_success else '❌ FAILED'}")
    
    # Demo validation features
    print("\n🔍 DEMO: Validation Features")
    print("-" * 40)
    
    validation_tests = [
        {
            "test": "Invalid email format",
            "email": "invalid-email",
            "password": "test123",
            "name": "Test User"
        },
        {
            "test": "Short password",
            "email": "test@example.com",
            "password": "123",
            "name": "Test User"
        },
        {
            "test": "Empty name",
            "email": "test2@example.com",
            "password": "test123",
            "name": ""
        }
    ]
    
    for i, test in enumerate(validation_tests, 1):
        print(f"\n{i}. Testing: {test['test']}")
        success, message = auth.register_user(
            email=test['email'],
            password=test['password'],
            name=test['name']
        )
        print(f"   Result: {'❌ CORRECTLY FAILED' if not success else '⚠️  UNEXPECTED SUCCESS'}")
        print(f"   Message: {message}")
    
    # Show current users
    print("\n👥 DEMO: Current Users in System")
    print("-" * 40)
    
    users = auth.load_users()
    for i, (username, user_data) in enumerate(users.items(), 1):
        print(f"\n{i}. Username: {username}")
        print(f"   Name: {user_data.get('name', 'N/A')}")
        print(f"   Email: {user_data.get('email', 'N/A')}")
        print(f"   Role: {user_data.get('role', 'N/A')}")
        print(f"   Department: {user_data.get('department', 'N/A')}")
        print(f"   Created: {user_data.get('created_at', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("\n🌐 Access the web interface:")
    print("   • Sign-up: http://localhost:5000/signup")
    print("   • Login:   http://localhost:5000/login")
    print("   • Main:    http://localhost:5000/")

if __name__ == "__main__":
    demo_authentication_system()
