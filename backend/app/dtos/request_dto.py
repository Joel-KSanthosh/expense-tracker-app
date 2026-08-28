from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, model_validator


class UserCreate(BaseModel):
    f_name: str = Field(min_length=1, max_length=255)
    m_name: str = Field(default="", max_length=255)
    l_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: SecretStr = Field(min_length=8)
    confirm_password: SecretStr = Field(min_length=8)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def verify_passwords_match(self) -> "UserCreate":
        pw: str = self.password.get_secret_value()
        cpw: str = self.confirm_password.get_secret_value()

        if pw != cpw:
            raise ValueError("Passwords do not match.")
        if not any(c.isupper() for c in pw):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in pw):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in pw):
            raise ValueError("Password must contain at least one number.")
        if not any(c in "!@#$%^&*()_+-=" for c in pw):
            raise ValueError("Password must contain at least one special character.")

        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)
