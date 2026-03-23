# Authentication Setup Guide

This document explains how to add authentication to the Spending Tracker application for public deployment.

## Current State

The application is currently designed as a **single-user system** without authentication. All data is accessible to anyone who can reach the API.

## When to Add Authentication

Add authentication if you plan to:
- Deploy the application publicly
- Support multiple users
- Protect sensitive financial data from unauthorized access

## Recommended Approach

### Option 1: JWT-Based Authentication (Recommended)

**Pros:**
- Stateless authentication
- Works well with FastAPI
- Easy to implement
- Good for API-first applications

**Implementation Steps:**

1. **Install dependencies:**
```bash
cd backend
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

2. **Add to requirements.txt:**
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

3. **Create User model:**
```python
# backend/app/models/user.py
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

4. **Create authentication service:**
```python
# backend/app/services/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

5. **Add authentication dependency:**
```python
# backend/app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
```

6. **Add user_id to all models:**
```python
# Add to Transaction, Category, Account models
user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
```

7. **Protect routes:**
```python
@router.get("/transactions")
def list_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Filter by user_id
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
```

8. **Frontend: Store JWT token:**
```typescript
// frontend/src/lib/auth.ts
export const login = async (email: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  const data = await response.json()
  localStorage.setItem('token', data.access_token)
  return data
}

export const getToken = () => localStorage.getItem('token')

export const logout = () => localStorage.removeItem('token')
```

9. **Update API client to include token:**
```typescript
// frontend/src/lib/api.ts
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken()
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  })
  // Handle 401 errors
  if (response.status === 401) {
    logout()
    window.location.href = '/login'
  }
  return response.json()
}
```

### Option 2: OAuth2 with Third-Party Providers

Use services like Auth0, Clerk, or Supabase for managed authentication.

**Pros:**
- No password management
- Social login support
- Professional security
- Less code to maintain

**Cons:**
- External dependency
- Potential cost
- More complex setup

### Option 3: Session-Based Authentication

Traditional session-based auth with cookies.

**Pros:**
- Familiar pattern
- Built-in CSRF protection

**Cons:**
- Stateful (requires session storage)
- More complex with separate frontend/backend

## Database Migration

After adding User model and user_id columns:

```bash
cd backend
alembic revision --autogenerate -m "add_authentication"
alembic upgrade head
```

## Security Considerations

1. **Use environment variables for secrets:**
```python
# backend/app/config.py
class Settings(BaseSettings):
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
```

2. **Enable HTTPS in production**
3. **Implement rate limiting** (use slowapi)
4. **Add password requirements** (min length, complexity)
5. **Implement password reset flow**
6. **Add email verification**
7. **Enable CORS properly** (restrict origins)

## Testing Authentication

```python
# backend/tests/test_auth.py
def test_login_success(client, test_user):
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_route_without_token(client):
    response = client.get("/transactions")
    assert response.status_code == 401

def test_protected_route_with_token(client, auth_token):
    response = client.get(
        "/transactions",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

## Frontend Login Page Example

```tsx
// frontend/src/app/login/page.tsx
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { login } from '@/lib/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(email, password)
      router.push('/')
    } catch (error) {
      alert('Login failed')
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  )
}
```

## Deployment Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add password reset flow
- [ ] Enable email verification
- [ ] Set up monitoring for failed login attempts
- [ ] Configure CORS properly
- [ ] Add audit logging
- [ ] Implement session timeout

## Resources

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
