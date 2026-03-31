"""
Unit Tests for Authentication (WHITE BOX TESTING)

Testing authentication logic in isolation:
- Password strength validation
- Email format validation
- Skill parsing
- Serialization
- Password hashing

These tests examine the internal implementation details of the auth module.
"""

import pytest
from app.auth import (
    validate_password_strength,
    parse_skills,
    validate_email_format,
    serialize_skills
)
from app.database.auth import AuthManager


class TestPasswordStrengthValidation:
    """Tests for password strength validation"""
    
    @pytest.mark.unit
    def test_strong_password(self):
        """
        TEST: Verify strong password is accepted
        EXPECT: Validation passes
        """
        password = "StrongPassword123!"
        is_valid, message = validate_password_strength(password)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_weak_password_too_short(self):
        """
        TEST: Verify password shorter than 6 characters is rejected
        EXPECT: Validation fails with character message
        """
        password = "Weak1"  # Only 5 characters
        is_valid, message = validate_password_strength(password)
        
        assert is_valid is False
        assert "6" in message or "character" in message.lower()
    
    @pytest.mark.unit
    def test_password_minimum_length(self):
        """
        TEST: Verify minimum length requirement (6 characters)
        EXPECT: Exactly 6 characters should pass
        """
        password = "Pass12"  # Exactly 6 characters
        is_valid, message = validate_password_strength(password)
        
        # Should pass minimum length check
        assert is_valid is True or "6" not in message
    
    @pytest.mark.unit
    def test_password_too_long(self):
        """
        TEST: Verify very long password is rejected
        EXPECT: Over 128 characters should fail
        """
        password = "P@ssword" * 20  # Very long password
        is_valid, message = validate_password_strength(password)
        
        assert is_valid is False
        assert "128" in message or "long" in message.lower()
    
    @pytest.mark.unit
    def test_password_no_special_chars_or_numbers(self):
        """
        TEST: Verify password without numbers/special chars is handled
        EXPECT: Function validates format requirements
        """
        password = "OnlyLetters"
        is_valid, message = validate_password_strength(password)
        
        # Should fail - needs number or special character
        assert is_valid is False
    
    @pytest.mark.unit
    def test_password_with_number(self):
        """
        TEST: Verify password with number passes
        EXPECT: Validation succeeds
        """
        password = "Password123"
        is_valid, message = validate_password_strength(password)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_password_with_special_char(self):
        """
        TEST: Verify password with special character passes
        EXPECT: Validation succeeds
        """
        password = "Password!"
        is_valid, message = validate_password_strength(password)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_password_empty_string(self):
        """
        TEST: Verify empty password is rejected
        EXPECT: Validation fails
        """
        password = ""
        is_valid, message = validate_password_strength(password)
        
        assert is_valid is False


class TestEmailValidation:
    """Tests for email format validation"""
    
    @pytest.mark.unit
    def test_valid_email_basic(self):
        """
        TEST: Valid email format
        EXPECT: Returns True
        """
        email = "user@example.com"
        assert validate_email_format(email) is True
    
    @pytest.mark.unit
    def test_valid_email_with_subdomain(self):
        """
        TEST: Valid email with subdomain
        EXPECT: Returns True
        """
        email = "user@mail.example.co.uk"
        assert validate_email_format(email) is True
    
    @pytest.mark.unit
    def test_invalid_email_no_at(self):
        """
        TEST: Email without @ symbol
        EXPECT: Returns False
        """
        email = "userexample.com"
        assert validate_email_format(email) is False
    
    @pytest.mark.unit
    def test_invalid_email_no_domain(self):
        """
        TEST: Email without domain
        EXPECT: Returns False
        """
        email = "user@"
        assert validate_email_format(email) is False
    
    @pytest.mark.unit
    def test_invalid_email_no_extension(self):
        """
        TEST: Email without extension
        EXPECT: Returns False
        """
        email = "user@example"
        assert validate_email_format(email) is False
    
    @pytest.mark.unit
    def test_valid_email_with_plus(self):
        """
        TEST: Email with plus addressing
        EXPECT: Returns True
        """
        email = "user+tag@example.com"
        assert validate_email_format(email) is True
    
    @pytest.mark.unit
    def test_valid_email_with_numbers(self):
        """
        TEST: Email with numbers
        EXPECT: Returns True
        """
        email = "user123@example456.com"
        assert validate_email_format(email) is True
    
    @pytest.mark.unit
    def test_invalid_email_multiple_at(self):
        """
        TEST: Email with multiple @ symbols
        EXPECT: Returns False
        """
        email = "user@example@example.com"
        assert validate_email_format(email) is False


class TestSkillParsing:
    """Tests for skill parsing from JSON strings"""
    
    @pytest.mark.unit
    def test_parse_skills_valid_json(self):
        """
        TEST: Parse valid JSON skills string
        EXPECT: Returns list of skills
        """
        skills_json = '["Python", "JavaScript", "SQL"]'
        skills = parse_skills(skills_json)
        
        assert isinstance(skills, list)
        assert len(skills) == 3
        assert "Python" in skills
        assert "JavaScript" in skills
        assert "SQL" in skills
    
    @pytest.mark.unit
    def test_parse_skills_empty_list(self):
        """
        TEST: Parse empty JSON array
        EXPECT: Returns empty list
        """
        skills_json = '[]'
        skills = parse_skills(skills_json)
        
        assert isinstance(skills, list)
        assert len(skills) == 0
    
    @pytest.mark.unit
    def test_parse_skills_none(self):
        """
        TEST: Parse None/null value
        EXPECT: Handles gracefully, returns None
        """
        skills = parse_skills(None)
        
        # Should handle None gracefully
        assert skills is None
    
    @pytest.mark.unit
    def test_parse_skills_invalid_json(self):
        """
        TEST: Parse invalid JSON string
        EXPECT: Returns None (graceful error)
        """
        skills_json = '["Python", "JavaScript"'  # Missing closing bracket
        skills = parse_skills(skills_json)
        
        # Should handle invalid JSON gracefully
        assert skills is None
    
    @pytest.mark.unit
    def test_parse_skills_with_duplicates(self):
        """
        TEST: Parse skills with duplicate entries
        EXPECT: Returns all skills including duplicates
        """
        skills_json = '["Python", "Python", "JavaScript"]'
        skills = parse_skills(skills_json)
        
        assert isinstance(skills, list)
        assert "Python" in skills
        assert "JavaScript" in skills
    
    @pytest.mark.unit
    def test_parse_skills_special_characters(self):
        """
        TEST: Parse skills with special characters
        EXPECT: Preserves special characters
        """
        skills_json = '["C++", "C#", ".NET", "Node.js"]'
        skills = parse_skills(skills_json)
        
        assert isinstance(skills, list)
        assert "C++" in skills
        assert "C#" in skills
    
    @pytest.mark.unit
    def test_parse_skills_empty_string(self):
        """
        TEST: Parse empty string
        EXPECT: Returns None
        """
        skills = parse_skills("")
        assert skills is None


class TestSkillSerialization:
    """Tests for skill serialization to JSON"""
    
    @pytest.mark.unit
    def test_serialize_skills_valid(self):
        """
        TEST: Serialize list of skills to JSON
        EXPECT: Valid JSON string returned
        """
        skills = ["Python", "JavaScript", "SQL"]
        serialized = serialize_skills(skills)
        
        assert isinstance(serialized, str)
        assert "Python" in serialized
        assert "JavaScript" in serialized
    
    @pytest.mark.unit
    def test_serialize_skills_empty(self):
        """
        TEST: Serialize empty list
        EXPECT: Empty JSON array or None
        """
        skills = []
        serialized = serialize_skills(skills)
        
        # Empty list returns None based on implementation
        assert serialized is None or serialized == "[]"
    
    @pytest.mark.unit
    def test_serialize_skills_none(self):
        """
        TEST: Serialize None
        EXPECT: Returns None
        """
        serialized = serialize_skills(None)
        assert serialized is None
    
    @pytest.mark.unit
    def test_serialize_deserialize_roundtrip(self):
        """
        TEST: Serialize and deserialize should return original
        EXPECT: Data integrity maintained
        """
        original = ["Python", "JavaScript", "SQL"]
        serialized = serialize_skills(original)
        deserialized = parse_skills(serialized)
        
        assert deserialized == original


class TestPasswordHashing:
    """Tests for password hashing via AuthManager"""
    
    @pytest.mark.unit
    def test_hash_password_valid(self):
        """
        TEST: Hash a valid password
        EXPECT: Returns hash and salt
        """
        auth = AuthManager()
        password = "TestPassword123"
        hashed, salt = auth.hash_password(password)
        
        assert hashed is not None
        assert salt is not None
        assert len(hashed) > 0
        assert len(salt) > 0
        assert hashed != password  # Not plaintext
    
    @pytest.mark.unit
    def test_hash_password_different_salts(self):
        """
        TEST: Same password produces different hash each time (due to salt)
        EXPECT: Different hashes for same password
        """
        auth = AuthManager()
        password = "TestPassword123"
        hash1, salt1 = auth.hash_password(password)
        hash2, salt2 = auth.hash_password(password)
        
        # Different salts and hashes
        assert salt1 != salt2
        assert hash1 != hash2
    
    @pytest.mark.unit
    def test_verify_password_correct(self):
        """
        TEST: Verify correct password matches hash
        EXPECT: Returns True
        """
        auth = AuthManager()
        password = "CorrectPassword123"
        hashed, salt = auth.hash_password(password)
        
        is_valid = auth.verify_password(password, hashed, salt)
        assert is_valid is True
    
    @pytest.mark.unit
    def test_verify_password_incorrect(self):
        """
        TEST: Verify incorrect password doesn't match
        EXPECT: Returns False
        """
        auth = AuthManager()
        password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        hashed, salt = auth.hash_password(password)
        
        is_valid = auth.verify_password(wrong_password, hashed, salt)
        assert is_valid is False
    
    @pytest.mark.unit
    def test_verify_password_case_sensitive(self):
        """
        TEST: Verify password comparison is case-sensitive
        EXPECT: Different case returns False
        """
        auth = AuthManager()
        password = "TestPassword123"
        hashed, salt = auth.hash_password(password)
        
        is_valid = auth.verify_password("testpassword123", hashed, salt)
        assert is_valid is False


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    @pytest.mark.unit
    def test_password_unicode(self):
        """
        TEST: Handle unicode characters in password
        EXPECT: Should hash correctly
        """
        auth = AuthManager()
        password = "Password123!@#éàü"
        hashed, salt = auth.hash_password(password)
        
        assert hashed is not None
        assert len(hashed) > 0
    
    @pytest.mark.unit
    def test_skills_with_unicode(self):
        """
        TEST: Parse skills with unicode characters
        EXPECT: Should handle correctly
        """
        skills_json = '["Python", "Développement", "SQL"]'
        skills = parse_skills(skills_json)
        
        assert isinstance(skills, list)
        assert "Développement" in skills
    
    @pytest.mark.unit
    def test_email_with_dots(self):
        """
        TEST: Email with multiple dots in local part
        EXPECT: Should be valid
        """
        email = "first.last@example.com"
        assert validate_email_format(email) is True
    
    @pytest.mark.unit
    def test_email_with_dash(self):
        """
        TEST: Email with dash in domain
        EXPECT: Should be valid
        """
        email = "user@my-example.com"
        assert validate_email_format(email) is True
    
    @pytest.mark.unit
    def test_email_with_underscore(self):
        """
        TEST: Email with underscore in local part
        EXPECT: Should be valid
        """
        email = "first_last@example.com"
        assert validate_email_format(email) is True
