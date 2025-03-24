# run_tests.py
# A script to run all tests with coverage reporting
import os
import sys
import django
import subprocess
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    print("=" * 80)

def print_success(text):
    """Print a success message."""
    print(f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_error(text):
    """Print an error message."""
    print(f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Fore.YELLOW}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def main():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lessons_learned.settings')
    django.setup()
    
    print_header("Lessons Learned System Test Runner")
    print("This script will run all tests and generate coverage reports.\n")
    
    # Check if coverage is installed
    try:
        import coverage
    except ImportError:
        print_error("Coverage is not installed. Please install it with: pip install coverage")
        print("Continuing without coverage reporting...")
        has_coverage = False
    else:
        has_coverage = True
    
    if has_coverage:
        # Start coverage
        cov = coverage.Coverage(
            source=['accounts', 'lessons', 'projects'],
            omit=['*/migrations/*', '*/tests.py', '*/apps.py', '*/admin.py']
        )
        cov.start()
        print("Started coverage measurement")
    
    print_header("Running Account App Tests")
    accounts_result = subprocess.run(
        ['python', 'manage.py', 'test', 'accounts.tests'],
        capture_output=True,
        text=True
    )
    if accounts_result.returncode == 0:
        print_success("Accounts tests passed!")
    else:
        print_error("Accounts tests failed!")
        print(accounts_result.stdout)
        print(accounts_result.stderr)
    
    print_header("Running Projects App Tests")
    projects_result = subprocess.run(
        ['python', 'manage.py', 'test', 'projects.tests'],
        capture_output=True,
        text=True
    )
    if projects_result.returncode == 0:
        print_success("Projects tests passed!")
    else:
        print_error("Projects tests failed!")
        print(projects_result.stdout)
        print(projects_result.stderr)
    
    print_header("Running Lessons App Tests")
    lessons_result = subprocess.run(
        ['python', 'manage.py', 'test', 'lessons.tests'],
        capture_output=True,
        text=True
    )
    if lessons_result.returncode == 0:
        print_success("Lessons tests passed!")
    else:
        print_error("Lessons tests failed!")
        print(lessons_result.stdout)
        print(lessons_result.stderr)
    
    print_header("Running Integration Tests")
    integration_result = subprocess.run(
        ['python', 'manage.py', 'test', 'integration_tests'],
        capture_output=True,
        text=True
    )
    if integration_result.returncode == 0:
        print_success("Integration tests passed!")
    else:
        print_error("Integration tests failed!")
        print(integration_result.stdout)
        print(integration_result.stderr)
    
    if has_coverage:
        # Stop coverage and generate reports
        cov.stop()
        cov.save()
        
        print_header("Coverage Report")
        # Print coverage report to terminal
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print_success("\nHTML coverage report generated in 'htmlcov' directory")
        print("Open htmlcov/index.html in your browser to view the report")
    
    # Determine overall success
    all_passed = (
        accounts_result.returncode == 0 and
        projects_result.returncode == 0 and
        lessons_result.returncode == 0 and
        integration_result.returncode == 0
    )
    
    if all_passed:
        print_header("All tests passed successfully!")
    else:
        print_header("Some tests failed. Please check the output above for details.")

if __name__ == "__main__":
    main()