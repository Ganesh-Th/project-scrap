# Contributing to AI Review Intelligence System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/project-scrap.git
   cd project-scrap
   ```

3. **Set up development environment**:
   ```bash
   # Start required services
   docker-compose up -d postgres redis
   
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend setup
   cd ../frontend
   npm install
   ```

## Making Changes

### Branch Naming
- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`

### Commit Messages
Follow conventional commits:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `refactor: improve code structure`
- `test: add tests`

### Code Style

#### Python (Backend)
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

```python
# Good
def analyze_sentiment(review_text: str) -> Dict[str, float]:
    """Analyze sentiment of review text."""
    pass

# Bad
def f(x):
    pass
```

#### TypeScript (Frontend)
- Use TypeScript strict mode
- Functional components with hooks
- Props interfaces for all components

```typescript
// Good
interface ButtonProps {
  label: string;
  onClick: () => void;
}

export const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
  return <button onClick={onClick}>{label}</button>;
};

// Bad
export const Button = (props) => {
  return <button>{props.label}</button>;
};
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
Follow the [TESTING.md](TESTING.md) guide.

## Pull Request Process

1. **Create a branch** from `main`
2. **Make your changes** with clear commits
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit PR** with:
   - Clear description
   - Related issue number
   - Screenshots (for UI changes)

## Project Structure

```
project-scrap/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── tasks/    # Celery tasks
│   └── tests/        # Backend tests
├── frontend/         # Next.js frontend
│   ├── src/
│   │   ├── app/      # Pages
│   │   ├── components/ # React components
│   │   ├── lib/      # Utilities
│   │   └── types/    # TypeScript types
│   └── __tests__/    # Frontend tests
└── docs/             # Documentation
```

## Adding New Features

### Backend Feature
1. Add model in `app/models/`
2. Create schema in `app/schemas/`
3. Implement logic in `app/services/`
4. Add endpoint in `app/api/`
5. Write tests

### Frontend Feature
1. Define types in `src/types/`
2. Create component in `src/components/`
3. Add API call in `src/lib/api.ts`
4. Integrate in page
5. Style with Tailwind

## Common Tasks

### Adding a Database Model
```python
# backend/app/models/__init__.py
class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

### Adding an API Endpoint
```python
# backend/app/api/new_endpoint.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/new", tags=["new"])

@router.get("/")
def list_items():
    return {"items": []}
```

### Adding a UI Component
```typescript
// frontend/src/components/NewComponent.tsx
interface NewComponentProps {
  title: string;
}

export default function NewComponent({ title }: NewComponentProps) {
  return <div>{title}</div>;
}
```

## Questions?

- Open an issue for bugs
- Start a discussion for feature ideas
- Ask in pull request comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
