from pydantic import BaseModel, EmailStr, field_validator


class UserRequestAddDTO(BaseModel):
    email: EmailStr
    username: str
    password: str

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


class UserUpdateRequestDTO(BaseModel):
    email: EmailStr
    username: str


class UserDTO(UserUpdateRequestDTO):
    id: int


class UserPasswordOnlyDTO(BaseModel):
    password: str


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
