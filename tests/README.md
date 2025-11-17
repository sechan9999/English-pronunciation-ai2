# Test Suite

This directory contains the comprehensive test suite for the English Pronunciation AI system.

## 📁 Structure

```
tests/
├── conftest.py                              # Pytest fixtures and configuration
├── test_pronunciation_analyzer_example.py   # Example unit tests (REFERENCE)
├── README.md                                # This file
│
└── (TO BE IMPLEMENTED - See TEST_COVERAGE_ANALYSIS.md)
    ├── test_pronunciation_analyzer.py       # Full unit tests for PronunciationAnalyzer
    ├── test_interview_analyzer.py           # Full unit tests for InterviewAnalyzer
    ├── test_scoring_accuracy.py             # Scoring validation tests
    ├── test_edge_cases.py                   # Edge case and boundary tests
    ├── test_error_handling.py               # Error handling tests
    ├── test_audio_processing.py             # Audio file processing tests
    ├── test_api_comprehensive.py            # Comprehensive API tests
    ├── test_data_validation.py              # Input validation and security
    ├── test_performance.py                  # Performance benchmarks
    └── test_integration.py                  # End-to-end integration tests
```

## 🚀 Quick Start

### Installation

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-benchmark

# Or use requirements file (when created)
pip install -r requirements-test.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_pronunciation_analyzer_example.py

# Run tests in parallel (faster)
pytest -n auto

# Run only unit tests
pytest -m unit

# Run excluding slow tests
pytest -m "not slow"

# Run with verbose output
pytest -v -s
```

## 📊 Current Status

**Coverage:** ~35% (as of 2025-11-17)
**Target:** 80%+
**Test Count:** 2 integration test files (basic coverage)

See `TEST_COVERAGE_ANALYSIS.md` for detailed coverage analysis and improvement roadmap.

## ✅ Example Test Usage

The file `test_pronunciation_analyzer_example.py` serves as a **reference implementation** showing how to write comprehensive unit tests. It includes:

- Basic unit tests for each method
- Mocking external dependencies (Whisper, librosa)
- Parameterized tests
- Edge case testing
- Proper use of fixtures

**To run the example tests:**

```bash
pytest tests/test_pronunciation_analyzer_example.py -v
```

## 🎯 Testing Best Practices

### 1. Use Fixtures for Reusability

```python
def test_something(pronunciation_analyzer):
    # pronunciation_analyzer is provided by fixture
    result = pronunciation_analyzer.calculate_pronunciation_score(...)
    assert result['overall_score'] >= 0
```

### 2. Mock External Dependencies

```python
def test_with_mock(mock_whisper):
    # Whisper is mocked, no model loading needed
    analyzer = PronunciationAnalyzer()
    # Fast test execution!
```

### 3. Test One Thing Per Test

```python
# Good - focused test
def test_perfect_match_returns_100():
    analyzer = PronunciationAnalyzer()
    result = analyzer.calculate_pronunciation_score("hello", "hello")
    assert result['overall_score'] == 100.0

# Bad - testing too many things
def test_everything():
    # Tests multiple unrelated behaviors
```

### 4. Use Descriptive Names

```python
# Good
def test_pronunciation_score_handles_empty_string_gracefully():
    pass

# Bad
def test_score():
    pass
```

### 5. Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange: Set up test data
    analyzer = PronunciationAnalyzer()
    reference = "hello world"

    # Act: Execute the code
    result = analyzer.calculate_pronunciation_score(reference, reference)

    # Assert: Verify outcome
    assert result['overall_score'] == 100.0
```

## 🏷️ Test Markers

Tests can be marked with custom markers:

```python
@pytest.mark.unit
def test_unit_test():
    pass

@pytest.mark.integration
def test_integration_test():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.requires_audio
def test_with_real_audio():
    pass
```

Run specific markers:
```bash
pytest -m unit           # Only unit tests
pytest -m "not slow"     # Skip slow tests
pytest -m integration    # Only integration tests
```

## 📝 Writing New Tests

### Step 1: Choose the Right Test File

- `test_pronunciation_analyzer.py` - For PronunciationAnalyzer methods
- `test_interview_analyzer.py` - For InterviewAnalyzer methods
- `test_api_comprehensive.py` - For API endpoint tests
- `test_edge_cases.py` - For edge cases

### Step 2: Use Appropriate Fixtures

```python
def test_my_feature(pronunciation_analyzer, sample_pronunciation_result):
    # Use fixtures from conftest.py
    result = pronunciation_analyzer.generate_feedback(sample_pronunciation_result)
    assert "feedback" in result
```

### Step 3: Mock External Dependencies

```python
def test_my_feature(mock_whisper):
    # Whisper is already mocked by fixture
    analyzer = PronunciationAnalyzer()
    # Test without slow model loading
```

### Step 4: Assert Thoroughly

```python
def test_comprehensive_assertion():
    result = analyzer.calculate_pronunciation_score(ref, spoken)

    # Check structure
    assert 'overall_score' in result
    assert 'word_accuracy' in result

    # Check values
    assert 0 <= result['overall_score'] <= 100
    assert isinstance(result['mispronounced_words'], list)

    # Use helper
    assert_valid_pronunciation_result(result)  # From conftest.py
```

## 🔧 Available Fixtures

See `conftest.py` for all available fixtures. Common ones:

| Fixture | Description |
|---------|-------------|
| `pronunciation_analyzer` | PronunciationAnalyzer instance |
| `interview_analyzer` | InterviewAnalyzer instance |
| `mock_whisper` | Mocked Whisper model |
| `mock_librosa` | Mocked librosa functions |
| `temp_audio_file` | Temporary audio file path |
| `sample_pronunciation_result` | Sample test data |
| `api_client` | Flask test client |

## 📊 Coverage Goals

| Component | Current | Target | Priority |
|-----------|---------|--------|----------|
| pronunciation_analyzer.py | ~10% | 90% | 🔴 Critical |
| interview_analyzer.py | ~5% | 90% | 🔴 Critical |
| api.py | ~30% | 80% | 🟠 High |
| app.py | ~0% | 60% | 🟡 Medium |
| Overall | ~35% | 80% | - |

## 🐛 Debugging Tests

```bash
# Run with print statements visible
pytest -s

# Run with debugger on failure
pytest --pdb

# Run single test
pytest tests/test_file.py::TestClass::test_method

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x
```

## 📈 Continuous Integration

(To be set up)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 🎓 Learning Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/2.3.x/testing/)
- [Python Testing with pytest (Book)](https://pragprog.com/titles/bopytest/python-testing-with-pytest/)

## 🤝 Contributing

When adding new features:

1. Write tests FIRST (TDD approach recommended)
2. Ensure all tests pass before committing
3. Maintain or improve coverage
4. Add appropriate markers (@pytest.mark.unit, etc.)
5. Update this README if adding new test categories

## 📞 Questions?

See the main project documentation:
- `TEST_COVERAGE_ANALYSIS.md` - Detailed test coverage analysis
- `CLAUDE.md` - Project architecture and coding conventions
- `README.md` - Main project documentation
