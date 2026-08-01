from src.models.transaction import StatusEnum, TransactionBase


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int

    total_amount: float
    payment_status: StatusEnum
