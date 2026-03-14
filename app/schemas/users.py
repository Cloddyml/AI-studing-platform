from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRequestAddDTO(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=31, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Пароль не может быть пустым")
        return v


class UserAddDTO(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str


class UserUpdateRequestPatchDTO(BaseModel):
    email: EmailStr | None = None
    username: str = Field(min_length=3, max_length=31, pattern=r"^[a-zA-Z0-9_]+$")


class UserDTO(BaseModel):
    email: EmailStr
    username: str
    id: int


class UserPasswordOnlyDTO(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Пароль не может быть пустым")
        return v


class UserHashedPasswordOnlyDTO(BaseModel):
    hashed_password: str


class UserWithHashedPasswordDTO(UserDTO):
    hashed_password: str
    role: str


class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Пароль не может быть пустым")
        return v
