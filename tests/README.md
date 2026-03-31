# Job Application Tracker - Test Suite Documentation

This is a testing framework covering tests across 3 phases (Unit, Unit Validation, & Integration testing).

**Status:** Complete - 123/123 tests passing (100%)    
**Execution Time:** ~23 seconds  
**Project Progress:** 123/170 tests complete (72.4%)

---

## Quick Overview

| Phase |       Type      | Tests | Status | Focus          |
|-------|-----------------|-------|--------|----------------|
|   1   | Unit            |  37   |  100%  | Auth functions |
|   2   | Unit Validation |  45   |  100%  | Business logic |
|   3   | Integration     |  41   |  100%  | DB operations  |
|-----------------------------------------------------------|
| TOTAL :                  **123** **100%**                 |

---

## Quick Start Commands

### Run All Tests
```bash
python3 -m pytest tests/ -v
```

### Run Specific Phase
```bash
python3 -m pytest tests/test_unit_auth.py -v                    # Phase 1
python3 -m pytest tests/test_unit_validation.py -v              # Phase 2
python3 -m pytest tests/test_integration_users.py tests/test_integration_applications.py -v  # Phase 3
```

### Run Specific Test Class
```bash
python3 -m pytest tests/test_integration_applications.py::TestApplicationStatusTransitions -v
```

### Additional Options
```bash
python3 -m pytest tests/ -k "password" -v                 # Tests matching pattern
python3 -m pytest tests/ --cov=backend/app -v             # With coverage
python3 -m pytest tests/ -x -v                            # Stop on first failure
python3 -m pytest tests/ -vv --tb=short                   # Detailed output
```

---

## Test Files

```
tests/
├── conftest.py                          # Pytest fixtures & configuration
├── test_unit_auth.py                    # Phase 1: 37 auth tests
├── test_unit_validation.py              # Phase 2: 45 validation tests
├── test_integration_users.py            # Phase 3: 25 user DB tests
├── test_integration_applications.py     # Phase 3: 25 application DB tests
└── README.md                            # Testing Documentation
```

---

## Phase 1: Unit Auth Tests

**File:** `test_unit_auth.py`  
**Type:** WHITE BOX (isolated function testing)  
**Execution Time:** ~1.2 seconds

### Test Classes
- **TestPasswordStrengthValidation** (8 tests) - Password requirements
- **TestEmailValidation** (8 tests) - Email format validation
- **TestSkillParsing** (7 tests) - JSON skill parsing
- **TestSkillSerialization** (4 tests) - JSON skill serialization
- **TestPasswordHashing** (5 tests) - PBKDF2-SHA256 hashing with salt
- **TestEdgeCases** (5 tests) - Unicode and special characters

### Key Tests
Password strength validation (8-50 chars, special chars, numbers)  
Email format validation (RFC-compliant)  
Skill JSON parsing and serialization  
Password hashing with unique salts  
Edge cases (Unicode, special chars)

---

## Phase 2: Unit Validation Tests

**File:** `test_unit_validation.py`  
**Type:** WHITE BOX (business logic testing)  
**Execution Time:** ~1.5 seconds

### Test Classes
- **TestApplicationStatusTransitions** (8 tests) - Status flow validation
- **TestApplicationDateValidations** (6 tests) - Date range validation
- **TestApplicationFieldValidations** (13 tests) - Field constraints
- **TestApplicationStatistics** (9 tests) - Statistics calculations
- **TestApplicationHistoryValidation** (4 tests) - Status history audit trail
- **TestApplicationValidationEdgeCases** (5 tests) - Edge cases

### Key Tests
Application status transitions (applied → interviewing → accepted/rejected)  
Date validation (past, present, future, ranges)  
Field validation (required, length, enums)  
Statistics (success rate, rejection rate, response rate)  
Status history chronological ordering  
Special characters and Unicode handling

---

## Phase 3: Integration Tests

**Files:** `test_integration_users.py` (25 tests) + `test_integration_applications.py` (25 tests)  
**Type:** GREY BOX (db + business logic)  
**Database:** SQLite (5 tables with relationships)  
**Execution Time:** ~10.9 seconds

### User Integration Tests

#### TestUserRegistrationWorkflow (5 tests)
- User creation with validation
- Email uniqueness enforcement
- Profile auto-creation on registration
- Timestamp recording
- Password hashing verification

#### TestUserSessionManagement (4 tests)
- Session token generation
- Token uniqueness constraint
- Expiration date handling
- Cascade delete verification

#### TestUserDataIntegrity (4 tests)
- Email uniqueness constraint (UNIQUE)
- One-to-one user-profile relationship
- Cascade delete on user deletion
- Inactive user filtering

#### TestUserProfileOperations (4 tests)
- Profile field updates
- Timestamp tracking (updated_at)
- Nullable optional fields
- User retrieval with profile

#### TestUserQueryPerformance (5 tests)
- Email-based lookup efficiency
- ID-based lookup efficiency
- Error handling for nonexistent users
- Multiple sequential queries
- Result consistency

### Application Integration Tests (25 Tests)

#### TestApplicationCreation (3 tests)
- Application creation validation
- Initial status history creation
- Multiple applications per user

#### TestApplicationStatusTransitions (4 tests)
- Status change functionality
- Audit trail recording
- Chronological timestamp ordering
- Notes preservation

#### TestApplicationUpdates (3 tests)
- Field updates (salary, location, notes)
- Immutable field protection
- Independent updates isolation

#### TestApplicationDeletion (3 tests)
- Application deletion
- Cascade delete to status history
- User deletion cascading to applications

#### TestApplicationRetrieval (4 tests)
- Retrieve all applications
- Filter by status
- Date ordering (newest first)
- Direct ID lookup

#### TestApplicationStatistics (3 tests)
- Status aggregation/counting
- Success rate calculation
- Response rate calculation

---

## Database Schema

### Tables Tested
1. **users** - User accounts (email UNIQUE, password hashing, timestamps)
2. **user_profiles** - User profiles (1:1 with users, optional fields)
3. **job_applications** - Job applications (status tracking, audit trail)
4. **application_status_history** - Status audit log (chronological ordering)
5. **user_sessions** - Session tokens (expiration, cascade delete)

### Relationships Tested
- users → user_profiles (1:1, ON DELETE CASCADE)
- users → job_applications (1:N, ON DELETE CASCADE)
- users → user_sessions (1:N, ON DELETE CASCADE)
- job_applications → application_status_history (1:N, ON DELETE CASCADE)

---

## Pytest Configuration

### Available Fixtures (conftest.py)

**Database Setup**
- `test_db_path` - Path to test db
- `setup_test_db` - Initialize test db with schema
- `db_connection` - DB connection for each test
- `clear_db_tables` - Clear all tables before test

**Test Data**
- `sample_user_data` - Sample user data
- `sample_hashed_user` - Pre-created user with hashed password + profile
- `sample_job_application_data` - Sample application data
- `sample_application_with_user` - Complete application + user

**Mocking**
- `mock_api_responses` - Mock external API responses

### How to Use Fixtures
```python
def test_example(db_connection, sample_hashed_user):
    """Test with database connection and pre-created user"""
    user_id = sample_hashed_user['id']
    # Test code here
```

---

## Execution Metrics

|    Metric      |     Value    |
|----------------|--------------|
| Total Tests    | 123          |
| Passing        | 123 (100%)   |
| Failing        | 0            |
| Test Classes   | 16           |
| Fixtures       | 12+          |
| Test Code      | 2,200+ lines |
| Execution Time | ~23 s        |
| Phase 1 Time   | ~1.2 s       |
| Phase 2 Time   | ~1.5 s       |
| Phase 3 Time   | ~10.9 s      |

---

## ⚙️ Tech. Stack

- **Framework:** Pytest 4.6.9
- **Python:** 3.8.10
- **Database:** SQLite
- **Test Approach:** WHITE BOX -> WHITE BOX -> GREY BOX
- **Coverage:** Auth, validation, db operations

---

## Important Concepts

### Testing Approaches

**Phase 1-2:**
- Test internal logic & functions directly
- No db required
- Fast execution
- Focus on code correctness

**Phase 3:**
- Test with real db interactions
- DB manager classes used
- Medium speed
- Focus on integration

**Phase 4-5: BLACK BOX (Pending)**
- Test HTTP endpoints
- No implementation knowledge
- Focus on API contracts

### Password Security
- PBKDF2-SHA256 algorithm
- Unique salt per password
- Never stores plaintext
- Tested: both unit and integration

### Database Integrity
- Foreign key constraints enforced
- Cascade deletes verified
- Unique constraints tested
- Referential integrity validated

---

## Next Phases

### Phase 4: API Testing (50 tests)
- Authentication endpoints (25 tests)
- Application endpoints (25 tests)
- FastAPI TestClient
- BLACK BOX approach
- Estimated: 2-3 hours

### Phase 5: E2E Testing (15 tests)
- Complete user workflows
- End-to-end scenarios
- Estimated: 1-2 hours

**Progress:** 123/170 tests complete (72.4%)

---

## Troubleshooting

### If Tests Won't Run
```bash
# Install pytest
pip install pytest==4.6.9 pytest-asyncio

# Verify Python version (need 3.8+)
python3 --version

# Debug test collection
python3 -m pytest tests/ --collect-only
```

### Database Issues
```bash
# Remove test database
rm /tmp/test_job_tracker.db

# Rerun tests (database auto-created)
python3 -m pytest tests/ -v
```

### Import Errors
```bash
# Set Python path e.g;
export PYTHONPATH=/home/monicadhieu/DMMA/Job-Application-Tracker/backend:$PYTHONPATH

# Run tests
python3 -m pytest tests/ -v
```

---
