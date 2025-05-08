#!/usr/bin/env python
import os
import sys
import pytest
import argparse
import subprocess
import time


def setup_test_environment():
    """Set up the test environment."""
    print("Setting up test environment...")
    
    # Set environment variables for testing
    os.environ["TEST_DATABASE_URL"] = os.environ.get(
        "TEST_DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test_postgis_microservices"
    )
    
    # Check if PostGIS is available
    try:
        subprocess.run(
            ["psql", "-c", "SELECT PostGIS_Version();", os.environ["TEST_DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("PostGIS is available.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: PostGIS might not be available. Some tests may fail.")
    
    # Check if DuckDB is available
    try:
        import duckdb
        conn = duckdb.connect(":memory:")
        conn.execute("INSTALL spatial; LOAD spatial;")
        conn.close()
        print("DuckDB with spatial extension is available.")
    except Exception as e:
        print(f"Warning: DuckDB with spatial extension might not be available: {e}")
        print("Some tests may fail.")


def run_tests(args):
    """Run the tests."""
    # Set up test environment
    setup_test_environment()
    
    # Build pytest arguments
    pytest_args = []
    
    # Add test files or directories
    if args.test_path:
        pytest_args.extend(args.test_path)
    else:
        pytest_args.append("tests/")
    
    # Add verbosity
    if args.verbose:
        pytest_args.append("-v")
    
    # Add coverage
    if args.coverage:
        pytest_args.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
    
    # Add xvs flag
    if args.xvs:
        pytest_args.append("-xvs")
    
    # Add markers
    if args.markers:
        for marker in args.markers:
            pytest_args.append(f"-m {marker}")
    
    # Print command
    print(f"Running: pytest {' '.join(pytest_args)}")
    
    # Run tests
    start_time = time.time()
    result = pytest.main(pytest_args)
    end_time = time.time()
    
    # Print summary
    print(f"\nTests completed in {end_time - start_time:.2f} seconds.")
    
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests for the application.")
    parser.add_argument("test_path", nargs="*", help="Path to test file or directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--xvs", action="store_true", help="Run with -xvs flag")
    parser.add_argument("-m", "--markers", nargs="+", help="Run tests with specific markers")
    
    args = parser.parse_args()
    sys.exit(run_tests(args))
