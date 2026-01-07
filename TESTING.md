# AiRoHire Testing Framework

This document describes the comprehensive testing framework implemented for the AiRoHire video call participant management system.

## Overview

The testing framework provides complete coverage for both frontend and backend components without modifying any existing application files. It includes unit tests, integration tests, API endpoint tests, model validation tests, and performance testing.

## Test Structure

```
video-call-assignment/
├── frontend/src/tests/           # Frontend test files
│   ├── api.test.js              # API client tests
│   ├── App.integration.test.jsx  # Integration tests (existing)
│   ├── App.test.jsx             # Component tests (existing) 
│   ├── components.unit.test.jsx  # Unit tests (existing)
│   ├── setup.js                 # Test setup (existing)
│   └── utils.test.js            # Utility function tests
├── backend/tests/               # Backend test files
│   ├── __init__.py              # Test package init (existing)
│   ├── conftest.py              # Test fixtures (existing)
│   ├── test_conftest.py         # Enhanced test configuration
│   ├── test_api_comprehensive.py        # Comprehensive API tests
│   ├── test_models_comprehensive.py     # Comprehensive model tests
│   ├── test_main.py             # Main app tests (existing)
│   └── test_participants.py     # Participant tests (existing)
├── run_all_tests.sh            # Master test runner script
└── backend/run_tests.py        # Backend-specific test runner
```

## Frontend Testing

### Technologies Used
- **Vitest**: Fast testing framework
- **React Testing Library**: Component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **jsdom**: DOM environment simulation
- **MSW**: API mocking for integration tests

### Test Categories

#### 1. API Client Tests (`api.test.js`)
Tests all API client functions including:
- `fetchParticipants()` - Get participants list with pagination and search
- `fetchParticipantCount()` - Get total participant count
- `fetchParticipant()` - Get single participant details
- `updateParticipantMicrophone()` - Update microphone status
- `updateParticipantCamera()` - Update camera status  
- `updateParticipantStatus()` - Update online status
- Error handling scenarios
- Network failure simulation
- Timeout handling
- Configuration validation

#### 2. Integration Tests (`App.integration.test.jsx`)
Full application workflow testing:
- Component rendering and initialization
- Search functionality with real API calls
- View mode switching (grid/list)
- Modal interactions
- Microphone/camera control updates
- Error state handling
- Loading state verification
- Pagination testing

#### 3. Unit Tests (`utils.test.js`)
Individual component and utility testing:
- Participant card component rendering
- Audio visualizer functionality
- Search component behavior
- View toggle component
- Modal component interactions
- localStorage/sessionStorage utilities
- Date formatting utilities
- String manipulation utilities
- Array operations
- Error boundary simulation
- Performance considerations

### Running Frontend Tests

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies
npm install

# Run all tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui

# Run specific test file
npm run test api.test.js
```

## Backend Testing

### Technologies Used
- **pytest**: Python testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: Async HTTP client for testing
- **pytest-cov**: Coverage reporting
- **SQLAlchemy**: Database testing with SQLite
- **FastAPI TestClient**: API endpoint testing

### Test Categories

#### 1. API Endpoint Tests (`test_api_comprehensive.py`)
Comprehensive API testing including:

**Health Endpoint**
- Basic health check
- Async health check

**Participants Endpoint**
- Get participants (empty database)
- Get participants with data
- Pagination with limit/offset
- Search functionality (name, email, role)
- Case-insensitive search
- Invalid parameter handling

**Participant Count Endpoint**
- Count with empty database
- Count with data
- Count with search filters

**Single Participant Endpoint**
- Get by ID
- Participant not found handling
- Invalid ID format handling

**Update Endpoints**
- Microphone status updates
- Camera status updates
- Online status updates
- Participant not found scenarios
- Invalid data handling

**Error Handling**
- CORS headers verification
- Database error simulation
- Malformed JSON requests
- Empty request bodies

**Data Validation**
- Correct data types
- Boolean field validation
- Field constraints

**Performance Testing**
- Large dataset pagination
- Search performance with multiple participants

**Async Testing**
- Async endpoint verification
- Async error handling

#### 2. Model Tests (`test_models_comprehensive.py`)
Database model validation:

**Participant Model Creation**
- Basic participant creation
- Default values testing
- Required fields enforcement
- String representation
- Field length constraints
- Email field validation
- Role field validation
- Boolean field combinations
- Avatar URL auto-generation
- Timestamp auto-setting

**Database Queries**
- Query all participants
- Query by ID, email, role
- Query by online/mic/camera status
- Multiple filter queries
- LIKE search queries
- Ordering and pagination
- Count queries

**Updates and Deletion**
- Update individual fields
- Update multiple fields
- Participant deletion
- Multiple participant deletion

**Database Integrity**
- ID uniqueness
- Email duplication handling
- Transaction rollbacks

#### 3. Test Configuration (`test_conftest.py`)
Enhanced test setup providing:
- Test database configuration
- Session management
- Dependency override setup
- Test client creation
- Sample data fixtures
- Helper functions for data creation

### Running Backend Tests

```bash
# Navigate to backend directory
cd backend/

# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

# Run specific test file
python -m pytest tests/test_api_comprehensive.py -v

# Run with performance analysis
python -m pytest tests/ --durations=10

# Use the custom test runner
python run_tests.py
```

## Test Runners

### Master Test Runner (`run_all_tests.sh`)
Comprehensive test execution for entire project:
- Checks prerequisites (Node.js, Python3)
- Installs dependencies automatically
- Runs frontend and backend tests
- Provides detailed reporting
- Generates coverage reports
- Offers troubleshooting guidance

```bash
# Make executable (if needed)
chmod +x run_all_tests.sh

# Run all tests
./run_all_tests.sh
```

### Backend Test Runner (`backend/run_tests.py`)
Specialized backend test execution:
- Multiple test configurations
- Individual test file execution
- Comprehensive test suites
- Coverage reporting (terminal and HTML)
- Performance analysis
- Test collection verification
- Detailed success/failure reporting

```bash
# Navigate to backend directory
cd backend/

# Run backend tests
python run_tests.py
```

## Coverage Reports

### Frontend Coverage
- Generated by Vitest with coverage provider
- Shows line, function, and branch coverage
- Available in terminal and HTML formats

### Backend Coverage
- Generated by pytest-cov
- Shows statement and missing line coverage
- Available in terminal and HTML formats
- HTML report in `backend/htmlcov/index.html`

## Test Data

### Frontend Mock Data
- Sample participants with varied configurations
- API response mocking with MSW
- Error scenario simulation
- Storage mocking (localStorage/sessionStorage)

### Backend Test Data
- SQLite test database (isolated per test)
- Sample participant fixtures
- Multiple participant scenarios
- Database transaction testing

## Error Scenarios Tested

### Frontend
- API network failures
- Timeout errors
- Malformed API responses
- Component render errors
- Storage quota exceeded
- Invalid user interactions

### Backend
- Database connection failures
- Invalid request data
- Missing participants
- Malformed JSON
- Authentication/authorization (if applicable)
- Concurrent request handling

## Performance Testing

### Frontend
- Large dataset rendering
- Memory usage optimization
- Event handler efficiency
- Component re-render minimization

### Backend
- Database query optimization
- Pagination performance
- Search query efficiency
- Concurrent request handling
- Memory usage patterns

## CI/CD Integration

The test framework is designed for easy CI/CD integration:

```yaml
# Example GitHub Actions workflow
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run All Tests
        run: ./run_all_tests.sh
```

## Maintenance

### Adding New Tests
1. **Frontend**: Add test files to `frontend/src/tests/`
2. **Backend**: Add test files to `backend/tests/`
3. Follow existing naming conventions
4. Use provided fixtures and utilities
5. Update this documentation

### Test Data Updates
- Update fixtures in `test_conftest.py` for backend
- Update mock data in test files for frontend
- Ensure test data reflects real-world scenarios

### Performance Monitoring
- Monitor test execution times
- Update performance tests as application grows
- Consider test parallelization for large test suites

## Troubleshooting

### Common Issues

#### Frontend
- **Tests not finding components**: Check import paths and component exports
- **API mocking not working**: Verify MSW setup in test files
- **Storage tests failing**: Ensure localStorage/sessionStorage mocks are configured

#### Backend
- **Database errors**: Check test database setup and cleanup
- **Import errors**: Verify PYTHONPATH includes backend directory
- **Async test failures**: Ensure proper async/await usage and pytest-asyncio setup

#### Both
- **Dependency issues**: Run `npm install` and `pip install -r requirements.txt`
- **Path issues**: Ensure running from correct directories
- **Permission issues**: Check file permissions on test runner scripts

### Debug Mode
```bash
# Frontend debug
npm run test -- --verbose

# Backend debug  
python -m pytest tests/ -v -s --tb=long

# Full debug
DEBUG=true ./run_all_tests.sh
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Naming**: Test names should describe what is being tested
3. **Arrange-Act-Assert**: Follow the AAA pattern
4. **Mock External Dependencies**: Don't rely on external services
5. **Test Edge Cases**: Include boundary conditions and error scenarios
6. **Regular Updates**: Keep tests in sync with application changes
7. **Performance Awareness**: Monitor test execution times
8. **Documentation**: Document complex test scenarios

This testing framework ensures high code quality, catches regressions early, and provides confidence for production deployments of the AiRoHire system.