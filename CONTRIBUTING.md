# Contributing to Lessons Learned System

Thank you for considering contributing to the Lessons Learned System! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How Can I Contribute?

### Reporting Bugs

- Before creating a bug report, check if the issue has already been reported
- Use the bug report template when submitting an issue
- Include detailed steps to reproduce the problem
- Describe the behavior you expected to see
- Include screenshots if applicable
- Specify your environment details (OS, browser, Django version, etc.)

### Suggesting Enhancements

- Use the feature request template when submitting suggestions
- Clearly describe the proposed feature and its benefits
- Provide examples of how the feature would be used
- Consider how the feature aligns with the project's goals

### Code Contributions

1. Fork the repository
2. Create a new branch for your contribution
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
   ```bash
   python run_tests.py
   ```
5. Submit a pull request

## Development Setup

Follow the installation instructions in the README.md file to set up the development environment.

## Style Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use 4 spaces for indentation (not tabs)
- Use docstrings to document functions and classes
- Keep line length to a maximum of 100 characters

### Commit Messages

- Use clear, descriptive commit messages
- Start with a short summary line (50 chars or less)
- Optionally, follow with a blank line and a more detailed description
- Use the imperative mood ("Add feature" not "Added feature")
- Reference issue numbers when applicable

Example:
```
Add pagination to lesson list view

- Implement Django pagination
- Add page navigation controls
- Maintain filter state between pages

Fixes #42
```

### Testing

- Write tests for new features and bug fixes
- Ensure all tests pass before submitting a pull request
- Aim for good test coverage

## Pull Request Process

1. Update the README.md or documentation with details of changes if applicable
2. Update the requirements.txt file if you've added new dependencies
3. Make sure all tests pass
4. The pull request will be reviewed by maintainers who may request changes
5. Once approved, your changes will be merged

## Questions?

If you have any questions or need clarification, please open an issue with the "question" label.

Thank you for contributing to making the Lessons Learned System better!
