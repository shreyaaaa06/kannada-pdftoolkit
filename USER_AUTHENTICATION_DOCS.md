# User Authentication System Documentation

## Overview
This document describes the comprehensive user authentication system implemented for the Kannada PDF Toolkit. The system supports both sign-up and login functionality with proper password security and session management.

## Features

### 1. User Registration (Sign-up)
- **Email-based registration**: Users can create accounts using their email address
- **Password security**: Passwords are hashed using PBKDF2-HMAC-SHA256 with salt
- **Form validation**: Client-side and server-side validation for all inputs
- **Duplicate prevention**: Prevents registration with already existing emails
- **Optional fields**: Government employees can provide additional information

### 2. User Login
- **Dual login support**: Users can log in with either email or username
- **Secure authentication**: Password verification against hashed passwords
- **Session management**: Flask sessions with secure tokens
- **Auto-login after registration**: Seamless user experience

### 3. Security Features
- **Password hashing**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Salt generation**: Unique salt for each password
- **Session tokens**: Secure URL-safe tokens for session management
- **Session expiration**: 8-hour session timeout with activity tracking
- **Password strength validation**: Client-side password strength checker

## File Structure

```
├── utils/
│   └── auth.py                 # Authentication manager with all auth logic
├── templates/
│   ├── login.html             # Login page with email/username support
│   └── signup.html            # Registration page with validation
├── app.py                     # Flask routes for /login and /signup
├── users.json                 # User database (JSON format)
├── sessions.json              # Active sessions storage
└── test_auth_system.py        # Comprehensive test suite
```

## API Endpoints

### 1. Sign-up Page
- **URL**: `/signup`
- **Methods**: GET, POST
- **Purpose**: User registration

#### POST Parameters:
- `email` (required): User's email address
- `password` (required): User's password (min 6 characters)
- `confirm_password` (required): Password confirmation
- `name` (required): User's full name
- `employee_id` (optional): Government employee ID
- `department` (optional): Department name
- `designation` (optional): Job designation

### 2. Login Page
- **URL**: `/login`
- **Methods**: GET, POST
- **Purpose**: User authentication

#### POST Parameters:
- `username` (required): Email address OR username
- `password` (required): User's password

### 3. Logout
- **URL**: `/logout`
- **Methods**: GET
- **Purpose**: End user session

## Database Schema

### User Object Structure
```json
{
  "username": {
    "email": "user@example.com",
    "password_hash": "hashed_password_with_salt",
    "name": "ಬಳಕೆದಾರ ಹೆಸರು",
    "employee_id": "EMP001",
    "department": "ವಿಭಾಗ",
    "designation": "ಹುದ್ದೆ",
    "role": "user",
    "created_at": "2025-08-07T12:00:00",
    "is_verified": false,
    "last_login": "2025-08-07T13:00:00"
  }
}
```

### Session Object Structure
```json
{
  "session_token": {
    "username": "user123",
    "created_at": "2025-08-07T12:00:00",
    "expires_at": "2025-08-07T20:00:00",
    "last_activity": "2025-08-07T13:00:00"
  }
}
```

## Authentication Manager Methods

### Core Methods
- `register_user()`: Register new user with validation
- `authenticate_user()`: Authenticate by username
- `authenticate_user_by_email()`: Authenticate by email
- `email_exists()`: Check if email is already registered
- `create_session()`: Create new session token
- `validate_session()`: Validate and refresh session
- `logout_session()`: End user session

### Security Methods
- `hash_password()`: Hash password with salt
- `verify_password()`: Verify password against hash
- `clean_expired_sessions()`: Remove expired sessions

## UI Features

### Sign-up Page
- **Responsive design**: Works on desktop and mobile
- **Real-time validation**: Password strength indicator
- **Password matching**: Confirms password match
- **Email validation**: Proper email format checking
- **Loading states**: Visual feedback during registration
- **Kannada support**: Full Kannada language interface

### Login Page
- **Dual input support**: Email or username login
- **Auto-focus**: Improves user experience
- **Error handling**: Clear error messages in Kannada
- **Guest access**: Option to continue without login
- **Sign-up link**: Easy navigation to registration

## Validation Rules

### Email
- Must be valid email format
- Must be unique (not already registered)

### Password
- Minimum 6 characters
- Strength indicator shows:
  - Weak: Basic requirements not met
  - Medium: Some complexity requirements met
  - Strong: All complexity requirements met

### Name
- Minimum 2 characters
- Only letters and spaces allowed
- Supports Kannada characters

## Error Messages (Kannada)

```
- "ಅಮಾನ್ಯ ಇಮೇಲ್ ವಿಳಾಸ" - Invalid email address
- "ಈ ಇಮೇಲ್ ವಿಳಾಸ ಈಗಾಗಲೇ ನೋಂದಾಯಿಸಲಾಗಿದೆ" - Email already registered
- "ಪಾಸ್‌ವರ್ಡ್ ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳಿರಬೇಕು" - Password minimum 6 characters
- "ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ" - Passwords don't match
- "ಮಾನ್ಯವಾದ ಹೆಸರು ನಮೂದಿಸಿ" - Enter valid name
```

## Success Messages (Kannada)

```
- "ಖಾತೆ ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ! ನಿಮ್ಮ ಬಳಕೆದಾರ ಹೆಸರು: {username}" - Account created successfully
```

## Testing

Run the test suite to verify functionality:
```bash
python test_auth_system.py
```

The test covers:
1. Valid user registration
2. Duplicate email prevention
3. Invalid email handling
4. Password length validation
5. Email-based login
6. Wrong password handling

## Security Considerations

1. **Password Storage**: Never store plaintext passwords
2. **Session Security**: Use secure, random session tokens
3. **Input Validation**: Always validate on both client and server
4. **SQL Injection**: Using JSON storage mitigates SQL injection
5. **Session Timeout**: Automatic session expiration for security
6. **HTTPS**: Should be used in production (not implemented in development)

## Future Enhancements

1. **Email Verification**: Send verification emails after registration
2. **Password Reset**: Allow users to reset forgotten passwords
3. **Two-Factor Authentication**: Add 2FA for enhanced security
4. **Account Management**: Allow users to update their profiles
5. **Admin Panel**: Administrative interface for user management
6. **Database Migration**: Move from JSON to proper database (SQLite/PostgreSQL)
7. **Rate Limiting**: Prevent brute force attacks
8. **Password Policy**: Enforce stronger password requirements

## Deployment Notes

1. Change the Flask secret key in production
2. Use HTTPS in production environment
3. Consider using a proper database instead of JSON files
4. Implement proper logging for security events
5. Add backup and recovery procedures for user data
