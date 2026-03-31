# Contributing Guide

Welcome to the **Job Application Tracker** project!

This guide explains how to collaborate, commit code, and report issues. All templates are included here for convenience.

---

## Table of Contents

* [Project Workflow](#project-workflow)
* [Getting Started](#getting-started)
* [Branching Strategy](#branching-strategy)
* [Commit Guidelines](#commit-guidelines)
* [Pull Request Process](#pull-request-process)
* [Testing](#testing)
* [Code Style](#code-style)
* [Documentation](#documentation)
* [Issue Templates](#issue-templates)
* [Code of Conduct](#code-of-conduct)

---

## Project Workflow

Use **GitHub flow** + **Agile development practices**:

1. Work in **feature branches** off `main`
2. Submit changes via **Pull Requests (PRs)**
3. Keep `main` branch stable and production-ready
4. All code must pass tests and reviews before merging
5. Track tasks and issues on GitHub

---

## Getting Started

### 1. Fork the Repository

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/m-dhieu/Job-Application_Tracker.git
cd Job-Application_Tracker
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Verify setup
python3 -m pytest tests/ -v
```

### 3. Add Upstream Remote

```bash
# Add original repo as upstream
git remote add upstream https://github.com/m-dhieu/Job-Application_Tracker.git

# Verify remotes
git remote -v
```

---

## Branching Strategy

- **`main`** → Stable branch (protected, production-ready)
- **`develop`** → Development integration branch (optional)
- **`feature/<name>`** → New features
- **`bugfix/<name>`** → Bug fixes
- **`hotfix/<name>`** → Urgent production fixes
- **`docs/<name>`** → Documentation updates
- **`test/<name>`** → Test additions

### Creating a Feature Branch

```bash
# Update main first
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/user-authentication
# or
git checkout -b bugfix/password-validation
```

### Branch Naming Conventions

- Use lowercase letters and hyphens
- Be descriptive but concise
- Start with issue number if available

Examples:
```
feature/add-email-notifications
bugfix/fix-cascade-delete-issue
docs/update-api-documentation
test/add-integration-tests
```

---

## Commit Guidelines

We follow **conventional commits** format for clear, semantic messages:

### Commit Types

- **`feat:`** – New feature
- **`fix:`** – Bug fix
- **`docs:`** – Documentation only
- **`test:`** – Adding/updating tests
- **`refactor:`** – Code refactoring (no feature/bug change)
- **`perf:`** – Performance improvement
- **`chore:`** – Maintenance, dependencies
- **`style:`** – Code style changes (formatting)

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Examples

```bash
# Feature commit
git commit -m "feat(auth): add JWT token generation and validation"

# Bug fix
git commit -m "fix(database): correct cascade delete behavior for applications"

# Documentation
git commit -m "docs(readme): add troubleshooting section"

# Tests
git commit -m "test(integration): add 25 application integration tests"

# Multiple lines (for complex changes)
git commit -m "feat(api): implement status history tracking

- Add application_status_history table
- Create API endpoints for status retrieval
- Add audit trail functionality
- Implement cascade delete on application deletion

Fixes #45"
```

### Commit Best Practices

- Keep commits atomic (one logical change per commit)
- Write descriptive messages in imperative mood
- Reference issue numbers when applicable
- Keep commit messages under 72 characters for subject line

---

## Pull Request Process

### Before Creating a PR

1. **Sync with upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests locally**
   ```bash
   python3 -m pytest tests/ -v
   ```

3. **Check code style**
   ```bash
   pycodestyle backend/app/
   black backend/app/
   ```

4. **Run full test suite**
   ```bash
   python3 -m pytest tests/ -v --tb=short
   ```

### Creating a PR

1. Push your branch to your fork
   ```bash
   git push origin feature/your-feature
   ```

2. Go to GitHub and click "New Pull Request"

3. Fill out the PR template (see below)

4. Link related issues using `Closes #ISSUE_NUMBER`

5. Request reviewers (at least 1)

### PR Review Process

- Code will be reviewed for:
  - Correctness and logic
  - Test coverage
  - Documentation completeness
  - Code style adherence
  - Performance considerations

- Address feedback and update your PR:
  ```bash
  git add .
  git commit -m "Address review feedback"
  git push origin feature/your-feature
  ```

- Merge only after approval and all checks pass

### Merging

- Use **Squash and merge** for small features
- Use **Create a merge commit** for larger changes
- Delete branch after merging

---

## Testing

### Test Coverage Requirements

-  All new features must include tests
-  Bug fixes should include regression tests
-  Minimum 80% code coverage required
-  All tests must pass before PR merge

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_unit_auth.py -v

# Run specific test class
python3 -m pytest tests/test_unit_auth.py::TestPasswordValidation -v

# Run with coverage report
python3 -m pytest tests/ --cov=app --cov-report=html

# Run in watch mode (requires pytest-watch)
ptw tests/
```

### Test Organization

```
tests/
├── conftest.py                    # shared fixtures & configuration
├── test_unit_auth.py              # authentication unit tests
├── test_unit_validation.py        # validation unit tests
├── test_integration_users.py      # user integration tests
├── test_integration_applications.py  # app integration tests
└── README.md                      # testing documentation
```

### Writing Tests

- Use descriptive test names: `test_should_<action>_when_<condition>`
- Test one thing per test function
- Use fixtures for setup/teardown
- Include both happy path and edge cases

Example:
```python
def test_should_hash_password_with_pbkdf2_when_valid_password_provided():
    """Test that password is hashed using PBKDF2-SHA256"""
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
```

---

## Code Style

### Python

- Follow [PEP8](https://peps.python.org/pep-0008/)
- Use **Black** for formatting
- Use **pycodestyle** for linting
- Line length: 88 characters (Black default)

```bash
# Format code
black backend/app/

# Check style
pycodestyle backend/app/

# Auto-fix common issues
autopep8 --in-place --aggressive backend/app/*.py
```

### JavaScript

- Follow ESLint defaults
- Use consistent indentation (2 spaces)
- Use meaningful variable names

### General

- Use meaningful variable/function names
- Add type hints in Python
- Keep functions focused and small (< 20 lines ideally)
- Comment complex logic, not obvious code

### Code Review Checklist

- [ ] Follows project code style
- [ ] Functions are well-named and focused
- [ ] No hardcoded values (use constants/config)
- [ ] Error handling is appropriate
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Performance is acceptable

---

## Documentation

### Required Documentation

- **Docstrings** for all functions/classes
- **Inline comments** for complex logic
- **README updates** for new features
- **API documentation** for new endpoints

### Docstring Format

```python
def create_application(user_id: int, job_title: str, company_name: str) -> dict:
    """
    Create a new job application for a user.
    
    Args:
        user_id: ID of the user creating the application
        job_title: Title of the job position
        company_name: Name of the hiring company
    
    Returns:
        Dictionary containing the created application data
    
    Raises:
        ValueError: If user_id is invalid
        DatabaseError: If database operation fails
    """
```

### Updating Documentation

- Update README.md for new features
- Update API docs in tests/README.md
- Add architecture diagrams if needed
- Document breaking changes prominently

---

## Issue Templates

### Bug Report

```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should have happened?

## Actual Behavior
What actually happened?

## Screenshots / Error Logs
Attach screenshots or error logs if available.

## Environment
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.10]
- Branch: [e.g. main]

## Additional Context
Any other details that might help?
```

### Feature Request

```markdown
## Feature Description
Clear description of the feature you'd like to see.

## Problem Statement
What problem does this solve? Why is this needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Are there other ways to solve this?

## Additional Context
- Mockups or diagrams (if applicable)
- Related issues or discussions
- Any research or references
```

### Pull Request Template

```markdown
## Description
What does this PR do? Explain the changes and why they're needed.

## Related Issue
Closes #ISSUE_NUMBER

## Type of Change
- [ ] Feature
- [ ] Bug Fix
- [ ] Documentation
- [ ] Tests
- [ ] Chore

## Changes Made
- Change 1
- Change 2
- Change 3

## How Has This Been Tested?
Describe the testing steps you performed:
1. Test case 1
2. Test case 2

## Test Results
```
All 123 tests passed in 16.58 seconds
```

## Screenshots (if applicable)
Add images or logs demonstrating the change.

## Breaking Changes
Any breaking changes? List them here.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] New tests added/updated
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] No secrets or sensitive data committed
- [ ] Commits are well-described
- [ ] All tests pass locally
```

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and constructive in all interactions
- Welcome feedback and different opinions
- Focus on what's best for the community
- Show empathy toward other contributors

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Offensive comments related to personal characteristics
- Trolling or inflammatory behavior
- Any form of abuse

### Reporting Issues

If you witness or experience unacceptable behavior, please contact:
- Email: mdhieu@alustudent.com
- Create a private issue on GitHub

---

## Development Tips

### Local Development Workflow

```bash
# Start with fresh branch
git checkout main
git pull upstream main
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Test locally
python3 -m pytest tests/ -v

# Format code
black backend/app/

# Commit changes
git add .
git commit -m "feat(module): add new feature"

# Push to your fork
git push origin feature/my-feature

# Create PR on GitHub
```

### Debugging

```bash
# Run tests with detailed output
python3 -m pytest tests/ -v -s --tb=long

# Run specific test with print statements
python3 -m pytest tests/test_file.py::test_name -v -s

# Check import issues
python3 -c "import backend.app.main; print('OK')"
```

### Performance Testing

```bash
# Run tests with timing information
python3 -m pytest tests/ -v --durations=10

# Profile specific code
python3 -m cProfile -s cumulative script.py
```

---

## Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [PEP8 Style Guide](https://peps.python.org/pep-0008/)
- [Semantic Versioning](https://semver.org/)
- [Pytest Documentation](https://docs.pytest.org/)

---

## Questions or Need Help?

-  Check the [README.md](README.md) first
-  Read [tests/README.md](tests/README.md) for testing info
-  Open a discussion or issue on GitHub
-  Email: mdhieu@alustudent.com

---

## Thank You!

Thank you for contributing to the Job Application Tracker project! 🎉

By following this guide, we'll keep the project:
-  Organized and maintainable
-  Collaborative and inclusive
-  Professional and high-quality
-  Well-tested and documented

Happy coding! 

---

*Last Updated: March 31, 2026*
