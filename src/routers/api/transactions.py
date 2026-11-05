from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import get_session
from src.dependencies import get_current_user
from src.models import (
    Transaction,
    User,
)
from src.schemas.transaction import TransactionCreate, TransactionRead
from src.services.transaction import (
    create_transaction,
)

router = APIRouter()


@router.post("/transactions/", response_model=TransactionRead)
async def create_transaction_endpoint(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        new_transaction = await create_transaction(
            session=session, data=transaction, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return new_transaction


@router.get("/transactions/", response_model=list[TransactionRead])
async def read_transactions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    statement = select(Transaction)
    results = await session.exec(statement)
    output = results.all()

    return output
