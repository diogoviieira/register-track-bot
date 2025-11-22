# 🤝 Contributing

Thank you for considering contributing to the Telegram Finance Tracker Bot! This document provides guidelines and instructions for contributing.

## How Can I Contribute?

### 🐛 Reporting Bugs

Found a bug? Please create an issue with:

- **Clear title** - Describe the issue concisely
- **Steps to reproduce** - How can we see the bug?
- **Expected behavior** - What should happen?
- **Actual behavior** - What actually happens?
- **Environment** - OS, Python version, bot version
- **Screenshots/logs** - If applicable

### 💡 Suggesting Features

Have an idea? Open an issue with:

- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives** - Any other approaches considered?
- **Additional context** - Mockups, examples, etc.

### 🔧 Pull Requests

1. **Fork** the repository
2. **Create a branch** - `git checkout -b feature/your-feature-name`
3. **Make changes** - Write clean, documented code
4. **Test** - Ensure nothing breaks
5. **Commit** - Use clear commit messages
6. **Push** - `git push origin feature/your-feature-name`
7. **Open PR** - Describe your changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/register-track-bot.git
cd register-track-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set test bot token
export TELEGRAM_BOT_TOKEN="your_test_bot_token"

# Run the bot
python run_bot.py
```

## Code Style

- **Python**: Follow [PEP 8](https://pep8.org/)
- **Line length**: 100 characters max
- **Docstrings**: Use for all functions and classes
- **Type hints**: Preferred for function signatures
- **Comments**: Explain "why", not "what"

### Example

```python
def calculate_monthly_total(user_id: int, month: str, year: str) -> float:
    """
    Calculate total expenses for a user in a specific month.
    
    Args:
        user_id: Telegram user ID
        month: Month number (01-12)
        year: Year (YYYY format)
        
    Returns:
        Total amount as float
    """
    # Implementation
    pass
```

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add monthly budget limits
fix: resolve date parsing for February
docs: update deployment guide
refactor: simplify expense categorization
test: add multi-user isolation tests
```

Prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance

## Testing

Before submitting a PR:

```bash
# Run tests
python tests/test_multiuser.py
python tests/test_bot_features.py

# Test manually
python run_bot.py
# Test in Telegram with real interactions
```

## Areas for Contribution

### Priority Features

- [ ] Budget limits with notifications
- [ ] Recurring expense templates
- [ ] Data export to CSV/PDF
- [ ] Charts and visualizations
- [ ] Web dashboard
- [ ] Multi-currency support
- [ ] Receipt photo storage
- [ ] Expense categories customization

### Documentation

- [ ] Video tutorials
- [ ] Translation to other languages
- [ ] More usage examples
- [ ] API documentation

### Infrastructure

- [ ] Docker support
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Performance benchmarks

## Code Review Process

1. **Automated checks** - Must pass (if configured)
2. **Maintainer review** - Code quality, design, tests
3. **Discussion** - Address feedback and concerns
4. **Approval** - Merged when approved

## Questions?

- Open a [Discussion](https://github.com/diogoviieira/register-track-bot/discussions)
- Comment on relevant issues
- Reach out via issue comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve this project! 🙏
