# Contributing to Oracle Network Test

First off, thank you for considering contributing to Oracle Network Test! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible using our issue template.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- A clear and descriptive title
- A detailed description of the proposed enhancement
- Examples of how the enhancement would be used
- Why this enhancement would be useful to most users

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing code style
5. Issue that pull request!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/oracletest.git
cd oracletest
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py  # Web version
python cli.py  # CLI version
```

## Testing

Run tests with:
```bash
python -m pytest tests/
```

## Code Style

- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions small and focused
- Write descriptive variable names

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Project Structure

```
oracletest/
├── src/                  # Core modules
│   ├── config.py        # Configuration
│   ├── network_tester.py # Network testing logic
│   └── utils.py         # Utility functions
├── templates/           # HTML templates
├── tests/              # Test files
├── app.py              # Web application
├── cli.py              # CLI application
└── requirements.txt    # Python dependencies
```

## Questions?

Feel free to open an issue with your question or contact the maintainers directly.

Thank you for contributing!