# Contributing to Optimized Passage Embeddings

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### 1. Fork the Repository
- Fork the repository to your GitHub account
- Clone your fork locally

### 2. Set Up Development Environment
```bash
git clone https://github.com/YOUR_USERNAME/OptimizedPassageEmbeddings.git
cd OptimizedPassageEmbeddings
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
pre-commit install
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes
- Write clear, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Follow the existing code style

### 5. Test Your Changes
```bash
# Run tests
pytest

# Run linting
ruff check .

# Run pre-commit hooks
pre-commit run --all-files
```

### 6. Commit Your Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

### 7. Push and Create a Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with a clear description of your changes.

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and under 50 lines when possible

### Commit Messages
Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

### Example
```
feat: add support for custom embedding models
fix: resolve URL validation issue with special characters
docs: update installation instructions
```

## Testing Guidelines

### Writing Tests
- Write tests for all new functionality
- Aim for good test coverage
- Use descriptive test names
- Mock external dependencies

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/passage_embed

# Run specific test file
pytest tests/test_cli.py
```

## Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Use Google or NumPy docstring format
- Include examples in docstrings for complex functions

### README Updates
- Update README.md if you add new features
- Include usage examples for new functionality
- Update version numbers and requirements

## Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation is updated
- [ ] No merge conflicts
- [ ] Commit messages follow conventional format

### Pull Request Description
Include:
- Summary of changes
- Motivation for changes
- Any breaking changes
- Screenshots (if UI changes)
- Test instructions

## Getting Help

If you need help:
1. Check existing issues and pull requests
2. Create a new issue with a clear description
3. Join discussions in existing issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License. 