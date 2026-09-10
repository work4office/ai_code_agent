from ai_code_agent.routes import (
    APIRouter,
    status,
    SessionDep,
    Users,
    LoginRequest,
    HTTPException,
    select,
    timedelta,
    Token,
    verify_password,
    create_access_token,
    settings,
    get_current_refresh_user,
    setRefreshToken,
    deleteRefreshToken,
    Depends,
    Response,
    Annotated,
)
from ai_code_agent.schemas.auth import User

router = APIRouter(prefix="/auth")

access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


def authenticate_user(
    user: Users | None,
    password: str,
) -> Users | None:
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user: LoginRequest, response: Response, session: SessionDep) -> Token:
    user_data = session.exec(select(Users).where(Users.email == user.email)).first()
    authenticated = authenticate_user(user_data, user.password)

    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    setRefreshToken(response, refresh_token)
    id = authenticated.id if authenticated.id is not None else 0
    user_data = User(id=id, email=authenticated.email, name=authenticated.name)
    return Token(access_token=access_token, user=user_data)


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_access_token(
    current_user: Annotated[Users, Depends(get_current_refresh_user)],
) -> Token:
    """
    Reads the refresh token from the HTTP-Only cookie, validates it,
    and returns a fresh access token.
    """
    # Issue a new access token
    new_token_data = {"sub": current_user.email}
    new_access_token = create_access_token(
        data=new_token_data,
        expires_delta=access_token_expires,
    )
    id = current_user.id if current_user.id is not None else 0
    user_data = User(id=id, email=current_user.email, name=current_user.name)
    return Token(access_token=new_access_token, user=user_data)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """Logs the user out by deleting the refresh token cookie."""
    deleteRefreshToken(response)
    return {"detail": "Successfully logged out"}
