from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import FilterPage, UserList, UserPublic, UserSchema
from fast_zero.security import (
    get_current_user,
    get_current_user_by_token,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session):

    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        # abordagem apenas para estudo, não é recomendado para produção
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Usuário com esse nome já existe',
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Usuário com esse email já existe',
            )

    # abordagem apenas para estudo, poderia ser melhorado utilizando
    # desempacotamento de dicionário UserDB(**user.model_dump())

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    session: Session,
    current_user: CurrentUser,
    filter_user: Annotated[FilterPage, Query()],
):
    users = session.scalars(
        select(User).limit(filter_user.limit).offset(filter_user.offset)
    )
    return {'users': users}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session: Session, current_user: CurrentUser):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado'
        )
    return user_db


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para atualizar este usuário',
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Usuário com esse nome ou email já existe',
        )


@router.delete(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(
    user_id: int,
    session: Session,
    authorization: Annotated[str | None, Header()] = None,
):
    if authorization:
        scheme, _, token = authorization.partition(' ')

        if scheme.lower() != 'bearer' or not token:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        get_current_user_by_token(session, token)

    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado'
        )

    session.delete(user_db)
    session.commit()
    return user_db
