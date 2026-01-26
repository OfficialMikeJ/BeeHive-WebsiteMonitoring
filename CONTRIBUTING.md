# Contributing to BeeHive - Website Manager

Thank you for considering contributing to BeeHive! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

---

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/beehive-manager.git
   cd beehive-manager
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/beehive-manager.git
   ```

---

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn server:app --reload --port 8001
```

### Frontend Development

```bash
cd frontend

# Install dependencies
yarn install

# Run development server
yarn start
```

### MongoDB

Ensure MongoDB is running on `localhost:27017` or update the `MONGO_URL` in `backend/.env`.

---

## Making Changes

### Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

### Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add email notifications for downtime
fix: resolve 2FA QR code display issue
docs: update installation instructions
refactor: improve website monitoring logic
test: add tests for user authentication
```

---

## Submitting Changes

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub:
   - Provide a clear title and description
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure all tests pass

---

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** where possible
- Write **docstrings** for functions and classes
- Keep functions small and focused
- Use **async/await** for I/O operations

Example:
```python
async def get_website_status(website_id: str) -> Dict[str, Any]:
    """
    Get the current status of a website.
    
    Args:
        website_id: The unique identifier of the website
        
    Returns:
        Dictionary containing website status information
    """
    website = await db.websites.find_one({"id": website_id})
    return website
```

### JavaScript/React (Frontend)

- Use **functional components** with hooks
- Follow **React best practices**
- Use **meaningful variable names**
- Keep components small and reusable
- Add **data-testid** attributes for testing

Example:
```javascript
const WebsiteCard = ({ website, onCheck }) => {
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    setLoading(true);
    await onCheck(website.id);
    setLoading(false);
  };

  return (
    <Card data-testid={`website-card-${website.id}`}>
      <CardTitle>{website.name}</CardTitle>
      <Button onClick={handleCheck} disabled={loading}>
        Check Now
      </Button>
    </Card>
  );
};
```

### General Guidelines

- **No hardcoded values** - Use environment variables
- **Error handling** - Always handle errors gracefully
- **Security** - Never commit secrets or credentials
- **Performance** - Optimize database queries and API calls
- **Accessibility** - Ensure UI is accessible (ARIA labels, keyboard navigation)

---

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
yarn test
```

### Manual Testing Checklist

Before submitting a PR, manually test:

- [ ] Setup flow works correctly
- [ ] Login/logout functionality
- [ ] Website CRUD operations
- [ ] Monitoring checks work
- [ ] 2FA setup and verification
- [ ] User management (admin only)
- [ ] Theme toggle works
- [ ] Responsive design on mobile
- [ ] No console errors

---

## Areas for Contribution

We welcome contributions in the following areas:

### Features

- Automated scheduled monitoring
- Email/SMS notifications
- SSL certificate monitoring
- Multi-region monitoring
- Custom alert thresholds
- Webhook integrations
- API rate limiting

### Improvements

- Performance optimization
- UI/UX enhancements
- Better error messages
- Improved documentation
- Additional tests

### Bug Fixes

Check the [Issues](https://github.com/original-owner/beehive-manager/issues) page for known bugs.

---

## Questions?

If you have questions about contributing:

1. Check existing [Issues](https://github.com/original-owner/beehive-manager/issues)
2. Start a [Discussion](https://github.com/original-owner/beehive-manager/discussions)
3. Contact the maintainers

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

<div align="center">
  <p>Thank you for contributing to BeeHive! 🐝</p>
</div>
