# Vanity Gateway Tests

Unit tests for the vanity-gateway service and vg_io modules.

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_vanity_gateway.py
```

### Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Run using the test runner:
```bash
./tests/run_tests.py
```

## Test Structure

- `test_vanity_gateway.py` - Tests for the main FastAPI application
  - Authentication and authorization
  - Provider routing
  - Request forwarding for both `requests` and `langchain_openai` APIs
  - URL parameter handling and type conversion

- `test_vg_io_rqs.py` - Tests for the `vg_io.rqs` module
  - Request handling with the requests library
  - Response parsing
  - Error handling

- `test_vg_io_oai.py` - Tests for the `vg_io.oai` module
  - LangChain OpenAI integration
  - Message format conversion
  - Response formatting

## Test Coverage

All tests use mocking to avoid external API calls and ensure fast, reliable test execution.
