"""
JWT Token Handler

Manages JWT token creation, validation, and user claims.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

try:
    import jwt
except ImportError:
    jwt = None

try:
    from pydantic import BaseModel
except ImportError:
    # Minimal fallback
    class BaseModel:
        pass


logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    username: str
    email: str
    roles: list[str]
    permissions: list[str]


class JWTHandler:
    """JWT token management"""

    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = "HS256",
        expiration_hours: int = 24,
    ):
        """
        Initialize JWT handler.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            expiration_hours: Token expiration time in hours
        """
        # Use default if not provided
        if secret_key is None:
            secret_key = "your-secret-key-change-in-production"
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def create_token(
        self,
        user_id: str,
        username: str,
        email: str,
        roles: list[str],
        permissions: list[str],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT token.

        Args:
            user_id: User ID
            username: Username
            email: Email address
            roles: User roles
            permissions: User permissions
            expires_delta: Custom expiration time

        Returns:
            JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=self.expiration_hours)

        expire = datetime.utcnow() + expires_delta

        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        # Ensure secret_key is set before encoding
        if not self.secret_key:
            self.secret_key = "your-secret-key-change-in-production"

        encoded_jwt = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

        logger.info(f"Token created for user: {username}")
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

            user_id: str = payload.get("user_id")
            username: str = payload.get("username")
            email: str = payload.get("email")
            roles: list[str] = payload.get("roles", [])
            permissions: list[str] = payload.get("permissions", [])

            if not user_id or not username:
                return None

            token_data = TokenData(
                user_id=user_id,
                username=username,
                email=email,
                roles=roles,
                permissions=permissions,
            )

            return token_data

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh JWT token.

        Args:
            token: Current JWT token

        Returns:
            New token if refresh successful, None otherwise
        """
        token_data = self.verify_token(token)
        if not token_data:
            return None

        return self.create_token(
            user_id=token_data.user_id,
            username=token_data.username,
            email=token_data.email,
            roles=token_data.roles,
            permissions=token_data.permissions,
        )
