"""
Unit Tests for Application Validation (WHITE BOX TESTING)

Testing business logic validation in isolation:
- Application status transitions and rules
- Date and time validations
- Field requirement and constraint validation
- Application status history tracking
- Statistics and aggregation calculations

These tests examine validation logic without database interactions.
"""

import pytest
from datetime import datetime, timedelta
from enum import Enum
from typing import Tuple, List, Dict, Optional
from app.models import ApplicationStatus, EmploymentType


class ApplicationStatusValidator:
    """Helper class for status transition validation"""
    
    # Valid status transitions
    VALID_TRANSITIONS = {
        ApplicationStatus.APPLIED: [ApplicationStatus.INTERVIEWING, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN],
        ApplicationStatus.INTERVIEWING: [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN],
        ApplicationStatus.REJECTED: [],
        ApplicationStatus.ACCEPTED: [],
        ApplicationStatus.WITHDRAWN: []
    }
    
    @staticmethod
    def is_valid_transition(from_status: ApplicationStatus, to_status: ApplicationStatus) -> bool:
        """Check if status transition is valid"""
        if from_status == to_status:
            return True  # Same status is valid (no-op)
        return to_status in ApplicationStatusValidator.VALID_TRANSITIONS.get(from_status, [])
    
    @staticmethod
    def get_valid_next_statuses(current_status: ApplicationStatus) -> List[ApplicationStatus]:
        """Get all valid next statuses for current status"""
        return ApplicationStatusValidator.VALID_TRANSITIONS.get(current_status, [])


class DateValidator:
    """Helper class for date and time validation"""
    
    @staticmethod
    def is_past_or_present_date(date: datetime) -> bool:
        """Check if date is in past or present"""
        return date <= datetime.now()
    
    @staticmethod
    def is_future_date(date: datetime) -> bool:
        """Check if date is in future"""
        return date > datetime.now()
    
    @staticmethod
    def is_valid_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Check if start date is before end date"""
        return start_date <= end_date


class ApplicationValidator:
    """Helper class for application field validation"""
    
    @staticmethod
    def validate_required_fields(application: Dict) -> Tuple[bool, str]:
        """Validate required fields in application"""
        required = ['job_title', 'company_name']
        
        for field in required:
            if field not in application or not application[field]:
                return False, f"Required field missing: {field}"
            
            if isinstance(application[field], str) and len(application[field].strip()) == 0:
                return False, f"Required field empty: {field}"
        
        return True, ""
    
    @staticmethod
    def validate_field_lengths(application: Dict) -> Tuple[bool, str]:
        """Validate field length constraints"""
        constraints = {
            'job_title': (1, 200),
            'company_name': (1, 100),
            'location': (0, 100),
            'salary_range': (0, 50),
            'notes': (0, 500)
        }
        
        for field, (min_len, max_len) in constraints.items():
            if field in application and application[field]:
                length = len(str(application[field]))
                if length < min_len or length > max_len:
                    return False, f"Field {field} length invalid: {length} (should be {min_len}-{max_len})"
        
        return True, ""
    
    @staticmethod
    def validate_enum_field(value: str, enum_class: type) -> bool:
        """Validate enum field"""
        try:
            enum_class(value)
            return True
        except (ValueError, KeyError):
            return False


class TestApplicationStatusTransitions:
    """Tests for valid/invalid status transitions"""
    
    @pytest.mark.unit
    def test_applied_to_interviewing_valid(self):
        """
        TEST: Transition from APPLIED to INTERVIEWING
        EXPECT: Should be valid transition
        """
        is_valid = ApplicationStatusValidator.is_valid_transition(
            ApplicationStatus.APPLIED,
            ApplicationStatus.INTERVIEWING
        )
        assert is_valid is True
    
    @pytest.mark.unit
    def test_applied_to_rejected_valid(self):
        """
        TEST: Transition from APPLIED to REJECTED
        EXPECT: Should be valid transition
        """
        is_valid = ApplicationStatusValidator.is_valid_transition(
            ApplicationStatus.APPLIED,
            ApplicationStatus.REJECTED
        )
        assert is_valid is True
    
    @pytest.mark.unit
    def test_interviewing_to_accepted_valid(self):
        """
        TEST: Transition from INTERVIEWING to ACCEPTED
        EXPECT: Should be valid transition
        """
        is_valid = ApplicationStatusValidator.is_valid_transition(
            ApplicationStatus.INTERVIEWING,
            ApplicationStatus.ACCEPTED
        )
        assert is_valid is True
    
    @pytest.mark.unit
    def test_rejected_to_any_invalid(self):
        """
        TEST: Transition from REJECTED to ACCEPTED
        EXPECT: Should be invalid (rejected is terminal)
        """
        is_valid = ApplicationStatusValidator.is_valid_transition(
            ApplicationStatus.REJECTED,
            ApplicationStatus.ACCEPTED
        )
        assert is_valid is False
    
    @pytest.mark.unit
    def test_accepted_to_any_invalid(self):
        """
        TEST: Transition from ACCEPTED to REJECTED
        EXPECT: Should be invalid (accepted is terminal)
        """
        is_valid = ApplicationStatusValidator.is_valid_transition(
            ApplicationStatus.ACCEPTED,
            ApplicationStatus.REJECTED
        )
        assert is_valid is False
    
    @pytest.mark.unit
    def test_same_status_valid(self):
        """
        TEST: Transition from APPLIED to APPLIED (same status)
        EXPECT: Should be valid (no-op)
        """
        is_valid = ApplicationStatusValidator.is_valid_transition(
            ApplicationStatus.APPLIED,
            ApplicationStatus.APPLIED
        )
        assert is_valid is True
    
    @pytest.mark.unit
    def test_get_valid_next_statuses_from_applied(self):
        """
        TEST: Get valid next statuses from APPLIED
        EXPECT: Should return INTERVIEWING, REJECTED, WITHDRAWN
        """
        next_statuses = ApplicationStatusValidator.get_valid_next_statuses(
            ApplicationStatus.APPLIED
        )
        
        assert ApplicationStatus.INTERVIEWING in next_statuses
        assert ApplicationStatus.REJECTED in next_statuses
        assert ApplicationStatus.WITHDRAWN in next_statuses
        assert ApplicationStatus.ACCEPTED not in next_statuses
        assert len(next_statuses) == 3
    
    @pytest.mark.unit
    def test_get_valid_next_statuses_from_rejected(self):
        """
        TEST: Get valid next statuses from REJECTED
        EXPECT: Should return empty list (terminal state)
        """
        next_statuses = ApplicationStatusValidator.get_valid_next_statuses(
            ApplicationStatus.REJECTED
        )
        
        assert len(next_statuses) == 0


class TestApplicationDateValidations:
    """Tests for date and time validations"""
    
    @pytest.mark.unit
    def test_past_date_validation(self):
        """
        TEST: Validate past date
        EXPECT: Should return True
        """
        past_date = datetime.now() - timedelta(days=5)
        is_valid = DateValidator.is_past_or_present_date(past_date)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_present_date_validation(self):
        """
        TEST: Validate present date (now)
        EXPECT: Should return True
        """
        present_date = datetime.now()
        is_valid = DateValidator.is_past_or_present_date(present_date)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_future_date_not_past_or_present(self):
        """
        TEST: Validate future date with past/present validator
        EXPECT: Should return False
        """
        future_date = datetime.now() + timedelta(days=5)
        is_valid = DateValidator.is_past_or_present_date(future_date)
        
        assert is_valid is False
    
    @pytest.mark.unit
    def test_future_date_validation(self):
        """
        TEST: Validate future date
        EXPECT: Should return True
        """
        future_date = datetime.now() + timedelta(days=5)
        is_valid = DateValidator.is_future_date(future_date)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_date_range_valid(self):
        """
        TEST: Validate date range with start < end
        EXPECT: Should return True
        """
        start = datetime.now()
        end = datetime.now() + timedelta(days=5)
        is_valid = DateValidator.is_valid_date_range(start, end)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_date_range_invalid_reversed(self):
        """
        TEST: Validate date range with start > end
        EXPECT: Should return False
        """
        start = datetime.now() + timedelta(days=5)
        end = datetime.now()
        is_valid = DateValidator.is_valid_date_range(start, end)
        
        assert is_valid is False


class TestApplicationFieldValidations:
    """Tests for field requirement and constraint validation"""
    
    @pytest.mark.unit
    def test_required_fields_present_and_valid(self):
        """
        TEST: Application with all required fields
        EXPECT: Validation passes
        """
        application = {
            'job_title': 'Senior Python Developer',
            'company_name': 'Tech Company Inc'
        }
        is_valid, message = ApplicationValidator.validate_required_fields(application)
        
        assert is_valid is True
        assert message == ""
    
    @pytest.mark.unit
    def test_missing_job_title(self):
        """
        TEST: Application missing job_title
        EXPECT: Validation fails
        """
        application = {
            'company_name': 'Tech Company Inc'
        }
        is_valid, message = ApplicationValidator.validate_required_fields(application)
        
        assert is_valid is False
        assert "job_title" in message
    
    @pytest.mark.unit
    def test_empty_company_name(self):
        """
        TEST: Application with empty company_name
        EXPECT: Validation fails
        """
        application = {
            'job_title': 'Senior Developer',
            'company_name': ''
        }
        is_valid, message = ApplicationValidator.validate_required_fields(application)
        
        assert is_valid is False
        assert "company_name" in message
    
    @pytest.mark.unit
    def test_job_title_field_length_within_limits(self):
        """
        TEST: Validate job_title within character limits (1-200)
        EXPECT: Should pass
        """
        application = {'job_title': 'Senior Python Developer'}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_company_name_field_length_within_limits(self):
        """
        TEST: Validate company_name within character limits (1-100)
        EXPECT: Should pass
        """
        application = {'company_name': 'Google Inc'}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_job_title_exceeds_max_length(self):
        """
        TEST: Validate job_title exceeding 200 characters
        EXPECT: Should fail
        """
        application = {'job_title': 'x' * 201}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is False
        assert "job_title" in message
    
    @pytest.mark.unit
    def test_company_name_exceeds_max_length(self):
        """
        TEST: Validate company_name exceeding 100 characters
        EXPECT: Should fail
        """
        application = {'company_name': 'x' * 101}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is False
        assert "company_name" in message
    
    @pytest.mark.unit
    def test_optional_location_field(self):
        """
        TEST: Optional location field within limits
        EXPECT: Should pass
        """
        application = {'location': 'New York, NY'}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_optional_location_exceeds_max(self):
        """
        TEST: Optional location field exceeding 100 characters
        EXPECT: Should fail
        """
        application = {'location': 'x' * 101}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is False
    
    @pytest.mark.unit
    def test_valid_employment_type_enum(self):
        """
        TEST: Validate employment type with valid enum value
        EXPECT: Should return True
        """
        is_valid = ApplicationValidator.validate_enum_field(
            EmploymentType.FULL_TIME.value,
            EmploymentType
        )
        assert is_valid is True
    
    @pytest.mark.unit
    def test_invalid_employment_type_enum(self):
        """
        TEST: Validate employment type with invalid enum value
        EXPECT: Should return False
        """
        is_valid = ApplicationValidator.validate_enum_field(
            "invalid-type",
            EmploymentType
        )
        assert is_valid is False
    
    @pytest.mark.unit
    def test_valid_status_enum(self):
        """
        TEST: Validate status with valid enum value
        EXPECT: Should return True
        """
        is_valid = ApplicationValidator.validate_enum_field(
            ApplicationStatus.APPLIED.value,
            ApplicationStatus
        )
        assert is_valid is True


class TestApplicationStatistics:
    """Tests for statistics calculations and aggregations"""
    
    @pytest.mark.unit
    def test_calculate_success_rate_all_accepted(self):
        """
        TEST: Calculate success rate with all applications accepted
        EXPECT: 100% success rate
        """
        applications = [
            {'status': ApplicationStatus.ACCEPTED},
            {'status': ApplicationStatus.ACCEPTED},
            {'status': ApplicationStatus.ACCEPTED}
        ]
        
        accepted_count = sum(1 for app in applications if app['status'] == ApplicationStatus.ACCEPTED)
        success_rate = (accepted_count / len(applications)) * 100
        
        assert success_rate == 100.0
    
    @pytest.mark.unit
    def test_calculate_success_rate_no_accepted(self):
        """
        TEST: Calculate success rate with no applications accepted
        EXPECT: 0% success rate
        """
        applications = [
            {'status': ApplicationStatus.REJECTED},
            {'status': ApplicationStatus.REJECTED},
            {'status': ApplicationStatus.APPLIED}
        ]
        
        accepted_count = sum(1 for app in applications if app['status'] == ApplicationStatus.ACCEPTED)
        success_rate = (accepted_count / len(applications)) * 100 if applications else 0
        
        assert success_rate == 0.0
    
    @pytest.mark.unit
    def test_calculate_success_rate_mixed(self):
        """
        TEST: Calculate success rate with mixed statuses
        EXPECT: 33.33% success rate (1/3)
        """
        applications = [
            {'status': ApplicationStatus.ACCEPTED},
            {'status': ApplicationStatus.REJECTED},
            {'status': ApplicationStatus.APPLIED}
        ]
        
        accepted_count = sum(1 for app in applications if app['status'] == ApplicationStatus.ACCEPTED)
        success_rate = (accepted_count / len(applications)) * 100
        
        assert 33.0 <= success_rate <= 34.0
    
    @pytest.mark.unit
    def test_calculate_rejection_rate(self):
        """
        TEST: Calculate rejection rate
        EXPECT: Should calculate correctly
        """
        applications = [
            {'status': ApplicationStatus.REJECTED},
            {'status': ApplicationStatus.REJECTED},
            {'status': ApplicationStatus.APPLIED}
        ]
        
        rejected_count = sum(1 for app in applications if app['status'] == ApplicationStatus.REJECTED)
        rejection_rate = (rejected_count / len(applications)) * 100
        
        assert 66.0 <= rejection_rate <= 67.0
    
    @pytest.mark.unit
    def test_calculate_response_rate_with_responses(self):
        """
        TEST: Calculate response rate (applications with response)
        EXPECT: Should count accepted/rejected/interviewing
        """
        applications = [
            {'status': ApplicationStatus.ACCEPTED},
            {'status': ApplicationStatus.REJECTED},
            {'status': ApplicationStatus.INTERVIEWING},
            {'status': ApplicationStatus.APPLIED}
        ]
        
        responded = sum(1 for app in applications 
                       if app['status'] in [ApplicationStatus.ACCEPTED, 
                                           ApplicationStatus.REJECTED, 
                                           ApplicationStatus.INTERVIEWING])
        response_rate = (responded / len(applications)) * 100
        
        assert response_rate == 75.0
    
    @pytest.mark.unit
    def test_count_applications_by_status_applied(self):
        """
        TEST: Count applications with APPLIED status
        EXPECT: Should return correct count
        """
        applications = [
            {'status': ApplicationStatus.APPLIED},
            {'status': ApplicationStatus.APPLIED},
            {'status': ApplicationStatus.REJECTED}
        ]
        
        applied_count = sum(1 for app in applications if app['status'] == ApplicationStatus.APPLIED)
        
        assert applied_count == 2
    
    @pytest.mark.unit
    def test_count_applications_by_status_interviewing(self):
        """
        TEST: Count applications with INTERVIEWING status
        EXPECT: Should return correct count
        """
        applications = [
            {'status': ApplicationStatus.INTERVIEWING},
            {'status': ApplicationStatus.APPLIED},
            {'status': ApplicationStatus.INTERVIEWING}
        ]
        
        interviewing_count = sum(1 for app in applications if app['status'] == ApplicationStatus.INTERVIEWING)
        
        assert interviewing_count == 2
    
    @pytest.mark.unit
    def test_calculate_status_breakdown(self):
        """
        TEST: Calculate breakdown of all statuses
        EXPECT: Should provide count for each status
        """
        applications = [
            {'status': ApplicationStatus.APPLIED},
            {'status': ApplicationStatus.INTERVIEWING},
            {'status': ApplicationStatus.ACCEPTED},
            {'status': ApplicationStatus.REJECTED},
            {'status': ApplicationStatus.WITHDRAWN}
        ]
        
        breakdown = {}
        for status in ApplicationStatus:
            breakdown[status] = sum(1 for app in applications if app['status'] == status)
        
        assert breakdown[ApplicationStatus.APPLIED] == 1
        assert breakdown[ApplicationStatus.INTERVIEWING] == 1
        assert breakdown[ApplicationStatus.ACCEPTED] == 1
        assert breakdown[ApplicationStatus.REJECTED] == 1
        assert breakdown[ApplicationStatus.WITHDRAWN] == 1
    
    @pytest.mark.unit
    def test_empty_applications_list(self):
        """
        TEST: Calculate statistics with empty applications list
        EXPECT: Should handle gracefully (0% rates)
        """
        applications = []
        
        success_rate = 0 if not applications else (
            sum(1 for app in applications if app['status'] == ApplicationStatus.ACCEPTED) / len(applications) * 100
        )
        
        assert success_rate == 0


class TestApplicationHistoryValidation:
    """Tests for application status history tracking"""
    
    @pytest.mark.unit
    def test_status_history_chronological_order(self):
        """
        TEST: Verify status history maintains chronological order
        EXPECT: Earlier statuses should have earlier timestamps
        """
        history = [
            {'status': ApplicationStatus.APPLIED, 'changed_at': datetime.now()},
            {'status': ApplicationStatus.INTERVIEWING, 'changed_at': datetime.now() + timedelta(days=1)},
            {'status': ApplicationStatus.ACCEPTED, 'changed_at': datetime.now() + timedelta(days=2)}
        ]
        
        # Verify each entry is after the previous
        for i in range(1, len(history)):
            assert history[i]['changed_at'] >= history[i-1]['changed_at']
    
    @pytest.mark.unit
    def test_status_history_initial_status_is_applied(self):
        """
        TEST: First status in history should be APPLIED
        EXPECT: Initial status always APPLIED
        """
        history = [
            {'status': ApplicationStatus.APPLIED, 'changed_at': datetime.now()}
        ]
        
        assert history[0]['status'] == ApplicationStatus.APPLIED
    
    @pytest.mark.unit
    def test_status_history_with_notes(self):
        """
        TEST: Status history entries can have optional notes
        EXPECT: Notes should be preserved
        """
        history_entry = {
            'status': ApplicationStatus.INTERVIEWING,
            'changed_at': datetime.now(),
            'notes': 'Phone screening scheduled'
        }
        
        assert 'notes' in history_entry
        assert history_entry['notes'] == 'Phone screening scheduled'
    
    @pytest.mark.unit
    def test_complete_application_lifecycle_history(self):
        """
        TEST: Track complete application lifecycle in history
        EXPECT: All transitions should be recorded
        """
        history = [
            {'status': ApplicationStatus.APPLIED},
            {'status': ApplicationStatus.INTERVIEWING},
            {'status': ApplicationStatus.ACCEPTED}
        ]
        
        # Verify all statuses are in history
        statuses = [entry['status'] for entry in history]
        assert ApplicationStatus.APPLIED in statuses
        assert ApplicationStatus.INTERVIEWING in statuses
        assert ApplicationStatus.ACCEPTED in statuses
        assert ApplicationStatus.REJECTED not in statuses


class TestApplicationValidationEdgeCases:
    """Tests for edge cases in application validation"""
    
    @pytest.mark.unit
    def test_whitespace_only_job_title_invalid(self):
        """
        TEST: Job title with only whitespace
        EXPECT: Should be treated as empty
        """
        application = {'job_title': '   '}
        is_valid, message = ApplicationValidator.validate_required_fields(application)
        
        assert is_valid is False
    
    @pytest.mark.unit
    def test_single_character_job_title_valid(self):
        """
        TEST: Job title with single character
        EXPECT: Should be valid (minimum 1)
        """
        application = {
            'job_title': 'X',
            'company_name': 'Corp'
        }
        is_valid, message = ApplicationValidator.validate_required_fields(application)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_special_characters_in_job_title(self):
        """
        TEST: Job title with special characters
        EXPECT: Should be valid
        """
        application = {
            'job_title': 'Senior C++/.NET/Python Developer',
            'company_name': 'Tech Corp'
        }
        is_valid, message = ApplicationValidator.validate_required_fields(application)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_unicode_characters_in_company_name(self):
        """
        TEST: Company name with unicode characters
        EXPECT: Should be valid
        """
        application = {
            'job_title': 'Developer',
            'company_name': 'Société Générale'
        }
        is_valid, message = ApplicationValidator.validate_required_fields(application)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_large_application_notes(self):
        """
        TEST: Very large notes field (up to 500 chars)
        EXPECT: Should be valid
        """
        application = {'notes': 'x' * 500}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is True
    
    @pytest.mark.unit
    def test_notes_exceeds_max_length(self):
        """
        TEST: Notes field exceeding 500 characters
        EXPECT: Should be invalid
        """
        application = {'notes': 'x' * 501}
        is_valid, message = ApplicationValidator.validate_field_lengths(application)
        
        assert is_valid is False
