# Testing Your Files.py API Endpoints

This guide explains the different ways you can test your `files.py` API endpoints in the backend.

## 🚀 Quick Start

### 1. **Unit Tests (Recommended for Development)**

Run comprehensive unit tests with pytest:

```bash
# Navigate to backend directory
cd backend

# Run all tests
./run_tests.sh

# Run only file-related tests
./run_tests.sh -f

# Run with coverage report
./run_tests.sh -c

# Run with verbose output
./run_tests.sh -v

# Run tests in parallel
./run_tests.sh -p
```

### 2. **Manual Testing (Quick API Testing)**

Test your API endpoints manually without pytest:

```bash
# Make sure your server is running first
python test_files_manual.py your_email@example.com your_password
```

### 3. **Integration Tests (Full System Testing)**

Run integration tests that test the actual running server:

```bash
# Run integration tests
python -m pytest tests/test_files_integration.py -v
```

## 📋 Prerequisites

Before running tests, make sure you have:

1. **Dependencies installed:**
   ```bash
   pip install -r requirements-dev.txt
   # or install manually:
   pip install pytest pytest-asyncio pytest-cov pytest-xdist httpx
   ```

2. **Database setup:**
   ```bash
   # Initialize database
   python init_database.py

   # Create test user
   python create_test_user.py
   ```

3. **Server running (for integration tests):**
   ```bash
   # Start your FastAPI server
   python run.py
   # or
   uvicorn app.main:app --reload
   ```

## 🧪 Test Types Explained

### **Unit Tests** (`tests/test_files.py`)
- **What they test:** Individual functions and endpoints in isolation
- **Dependencies:** Mocked (S3, document converter, database)
- **Speed:** Fast
- **Use case:** Development, CI/CD, regression testing

**Features:**
- ✅ All endpoints covered
- ✅ Error scenarios tested
- ✅ Mocked external services
- ✅ Fast execution
- ✅ No external dependencies

### **Manual Tests** (`test_files_manual.py`)
- **What they test:** Actual API calls to your running server
- **Dependencies:** Running server, real database, real S3
- **Speed:** Medium
- **Use case:** Quick API validation, debugging

**Features:**
- ✅ Real HTTP requests
- ✅ Actual database operations
- ✅ Real S3 interactions
- ✅ Easy to understand output
- ✅ No test framework needed

### **Integration Tests** (`tests/test_files_integration.py`)
- **What they test:** Full system integration
- **Dependencies:** Running server, real database, real S3
- **Speed:** Slow
- **Use case:** End-to-end testing, production validation

**Features:**
- ✅ Full system testing
- ✅ Real external services
- ✅ Production-like environment
- ✅ Comprehensive validation

## 🔧 Test Configuration

### **Environment Variables**
Make sure these are set for integration tests:
```bash
export DATABASE_URL="postgresql://user:password@localhost/dbname"
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
export S3_BUCKET_NAME="your_bucket"
```

### **Test Database**
Tests use an in-memory SQLite database by default. For PostgreSQL testing:
```python
# In conftest.py, change the database URL
DATABASE_URL = "postgresql://user:password@localhost/test_db"
```

## 📊 Running Specific Tests

### **Run Single Test Method**
```bash
# Run specific test method
pytest tests/test_files.py::TestFilesRoutes::test_upload_file_success -v

# Run tests matching pattern
pytest tests/test_files.py -k "upload" -v
```

### **Run Tests by Category**
```bash
# Run only fast tests
pytest -m "not slow" -v

# Run only unit tests
pytest -m "unit" -v

# Run only integration tests
pytest -m "integration" -v
```

### **Run Tests with Coverage**
```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## 🐛 Debugging Tests

### **Debug Failed Tests**
```bash
# Run with more verbose output
pytest -vvv --tb=long

# Run with print statements visible
pytest -s

# Run specific failing test
pytest tests/test_files.py::TestFilesRoutes::test_upload_file_success -vvv -s
```

### **Debug with pdb**
```python
# Add this line in your test where you want to debug
import pdb; pdb.set_trace()
```

### **Check Test Database**
```python
# In your test, print database contents
print("Files in DB:", session.query(File).all())
```

## 📝 Writing Your Own Tests

### **Basic Test Structure**
```python
def test_your_endpoint(self, client: TestClient, auth_headers, session: Session, test_user):
    """Test description"""
    # Setup
    file = File(filename="test.txt", owner_id=test_user.id)
    session.add(file)
    session.commit()

    # Execute
    response = client.get(f"/api/files/{file.id}", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
```

### **Testing with Mocks**
```python
def test_with_mock(self, client: TestClient, auth_headers):
    """Test with mocked external service"""
    with patch('app.services.s3_service.s3_service.upload_file') as mock_upload:
        mock_upload.return_value = True

        # Your test code here
        response = client.post("/api/files/upload", files=files, headers=auth_headers)

        # Verify mock was called
        mock_upload.assert_called_once()
```

## 🚨 Common Issues & Solutions

### **Import Errors**
```bash
# Make sure you're in the backend directory
cd backend

# Install dependencies
pip install -r requirements-dev.txt
```

### **Database Connection Issues**
```bash
# Check database is running
python check_db.py

# Reset test database
python init_database.py
```

### **S3 Connection Issues**
```bash
# Check AWS credentials
python check_config.py

# Test S3 connection
python s3_operations.py
```

### **Authentication Issues**
```bash
# Create test user
python create_test_user.py

# Check user exists
python -c "from app.crud import get_user_by_email; print(get_user_by_email('test@example.com'))"
```

## 📈 Test Coverage

Current test coverage includes:
- ✅ File upload (success & failure cases)
- ✅ File retrieval (list & individual)
- ✅ File download URL generation
- ✅ File deletion
- ✅ Share token creation
- ✅ File content updates
- ✅ Document conversion
- ✅ Quill content updates
- ✅ Error handling
- ✅ Authentication & authorization
- ✅ Pagination
- ✅ File format detection

## 🎯 Best Practices

1. **Run unit tests frequently** during development
2. **Use manual tests** for quick API validation
3. **Run integration tests** before deployment
4. **Mock external services** in unit tests
5. **Test both success and failure scenarios**
6. **Clean up test data** after tests
7. **Use descriptive test names**
8. **Group related tests** in test classes

## 🔗 Additional Resources

- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)
- [HTTPX Testing](https://www.python-httpx.org/testing/)

## 📞 Getting Help

If you encounter issues:
1. Check the error messages carefully
2. Verify all prerequisites are met
3. Check the test output for specific failures
4. Use the debugging techniques above
5. Check the FastAPI and pytest documentation

Happy testing! 🧪✨
