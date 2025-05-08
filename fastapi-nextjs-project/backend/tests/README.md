# Integration Test Suite

This directory contains integration tests for the FastAPI-NextJS application, focusing on the integration between Pydantic AI, GeoAlchemy, DuckDB, and PostGIS.

## Test Structure

The test suite is organized into the following files:

- `conftest.py`: Contains fixtures and setup for the tests
- `test_pydantic_geo_models.py`: Tests for Pydantic geospatial models
- `test_pydantic_ai_integration.py`: Tests for Pydantic AI integration with geospatial models
- `test_geoalchemy_postgis.py`: Tests for GeoAlchemy integration with PostGIS
- `test_duckdb_integration.py`: Tests for DuckDB integration
- `test_api_endpoints.py`: Tests for API endpoints
- `test_full_integration.py`: End-to-end tests for the full integration

## Prerequisites

To run the tests, you need:

1. PostgreSQL with PostGIS extension
2. DuckDB with spatial extension
3. Python dependencies installed

## Running the Tests

You can run the tests using the provided `run_tests.py` script:

```bash
# Run all tests
python run_tests.py

# Run specific test file
python run_tests.py tests/test_full_integration.py

# Run with coverage
python run_tests.py --coverage

# Run with verbose output
python run_tests.py -v

# Run tests with specific markers
python run_tests.py -m asyncio
```

## Test Database

The tests use a separate test database to avoid affecting your development or production database. By default, it uses:

```
postgresql+asyncpg://postgres:postgres@localhost:5432/test_postgis_microservices
```

You can override this by setting the `TEST_DATABASE_URL` environment variable.

## Test Data

The tests use sample data generated during the test run. The `conftest.py` file contains fixtures for creating sample GeoJSON data and other test resources.

## Coverage

To generate a coverage report, run:

```bash
python run_tests.py --coverage
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Troubleshooting

If you encounter issues with the tests:

1. Make sure PostgreSQL with PostGIS is running and accessible
2. Make sure DuckDB with spatial extension is installed
3. Check that all Python dependencies are installed
4. Look for specific error messages in the test output

## Adding New Tests

When adding new tests:

1. Follow the existing pattern for test organization
2. Use the fixtures provided in `conftest.py`
3. For async tests, use the `@pytest.mark.asyncio` decorator
4. For database tests, use the `db_session` fixture
5. For DuckDB tests, use the `duckdb_connection` fixture
