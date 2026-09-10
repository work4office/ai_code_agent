from ai_code_agent.routes import (
    APIRouter,
    status,
    SessionDep,
    Users,
    UserCreate,
    UserResponse,
    HTTPException,
    select,
    get_password_hash,
    Annotated,
    Depends,
    get_current_user,
)

router = APIRouter(prefix="/user")


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: SessionDep):
    hashed_password = get_password_hash(user.password)
    user_mapping = Users(
        name=user.name, email=user.email, hashed_password=hashed_password
    )
    session.add(user_mapping)
    session.commit()
    session.refresh(user_mapping)
    return user_mapping


@router.get("/all", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(
    session: SessionDep, current_user: Annotated[Users, Depends(get_current_user)]
):
    users = session.exec(select(Users)).all()
    return users


@router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_byId(
    id: int,
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    user = session.get(Users, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
