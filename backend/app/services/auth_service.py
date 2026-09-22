import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.config.settings import settings

logger = logging.getLogger("agripulse.services.auth")


class AuthService:
    """
    Service encapsulating user registration, credential verification,
    and JWT session token issuance.
    """

    @staticmethod
    def register_user(db: Session, request: UserRegisterRequest) -> User:
        """
        Registers a new user account if the email is not already taken.
        """
        normalized_email = request.email.lower().strip()
        existing_user = db.query(User).filter(User.email == normalized_email).first()
        if existing_user:
            logger.warning(f"Registration conflict: email '{normalized_email}' is already registered.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists."
            )

        password_hash = hash_password(request.password)
        new_user = User(
            name=request.name.strip(),
            email=normalized_email,
            password_hash=password_hash,
            is_active=True
        )

        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"Registered new user id={new_user.id} email='{new_user.email}'")
            return new_user
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user record: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user due to a database error."
            )

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Validates user credentials and returns the active User instance.
        """
        normalized_email = email.lower().strip()
        user = db.query(User).filter(User.email == normalized_email).first()

        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Failed authentication attempt for email '{normalized_email}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if not user.is_active:
            logger.warning(f"Authentication attempt on inactive user id={user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This user account is inactive. Please contact system support."
            )

        logger.info(f"Successfully authenticated user id={user.id} email='{user.email}'")
        return user

    @classmethod
    def generate_token_response(cls, user: User) -> TokenResponse:
        """
        Generates JWT token and creates standard TokenResponse.
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name
        }
        access_token = create_access_token(data=token_data)
        expires_in_seconds = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in_seconds,
            user=UserResponse.model_validate(user)
        )
