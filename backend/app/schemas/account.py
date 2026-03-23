from pydantic import BaseModel

from ..models.enums import AccountType


class AccountBase(BaseModel):
    name: str
    type: AccountType


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: str | None = None
    type: AccountType | None = None


class AccountOut(AccountBase):
    id: int

    class Config:
        from_attributes = True
