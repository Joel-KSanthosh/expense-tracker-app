from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserDetail(BaseModel):
    f_name: str
    m_name: str = Field(default="")
    l_name: str


class UserResponse(UserDetail):
    password: str
