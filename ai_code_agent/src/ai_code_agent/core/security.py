from ai_code_agent.core import (
    PasswordHash,
    settings,
    timedelta,
    timezone,
    datetime,
    jwt,
    UnknownHashError,
    Annotated,
    Depends,
    HTTPException,
    status,
    OAuth2PasswordBearer,
    InvalidTokenError,
    Users,
    TokenData,
    Response,
    SessionDep,
    select,
    Cookie,
    Optional,
)

password_hash = PasswordHash.recommended()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
COOKIE_NAME = settings.COOKIE_NAME
REFRESH_TOKEN_EXPIRE_DAYS: int = settings.REFRESH_TOKEN_EXPIRE_DAYS

algorithms: list[str] = [alg for alg in [ALGORITHM] if alg is not None]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except (UnknownHashError, TypeError, ValueError):
        return False


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def setRefreshToken(response: Response, refresh_token: str):
    """Set the refresh token in an HTTP-Only cookie"""
    response.set_cookie(
        key=COOKIE_NAME,
        value=refresh_token,
        httponly=True,  # Prevents frontend JavaScript from reading the cookie
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,  # Cookie lifetime in seconds
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        samesite="none",  # Protects against CSRF attacks
        secure=True,  # Set to True in production (forces HTTPS)
        path="/",
        # If frontend and backend are on completely different domains,
        # must use samesite="none" and secure=True
    )


def deleteRefreshToken(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        secure=True,
        samesite="none",
    )


def verify_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=algorithms)
        return payload
    except jwt.PyJWTError:
        return None


def get_user_from_token(
    token: str | None,
    session: SessionDep,
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = verify_token(token)
    email = (payload or {}).get("sub")

    if not email:
        raise credentials_exception

    user = session.exec(select(Users).where(Users.email == email)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


def get_email_from_token(token: str | None) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = verify_token(token)

    email = (payload or {}).get("sub")

    if not email:
        raise credentials_exception

    return email


def get_user_by_email(
    email: str,
    session: SessionDep,
) -> Users:
    user = session.exec(select(Users).where(Users.email == email)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    return user


def validate_active_user(user: Users) -> Users:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


def authenticate_token(
    token: str | None,
    session: SessionDep,
) -> Users:
    email = get_email_from_token(token)

    user = get_user_by_email(
        email=email,
        session=session,
    )

    return validate_active_user(user)


async def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Users:
    return authenticate_token(token, session)


async def get_current_refresh_user(
    session: SessionDep,
    refresh_token: Annotated[str | None, Cookie(alias=COOKIE_NAME)] = None,
) -> Users:
    return authenticate_token(
        refresh_token,
        session,
    )
