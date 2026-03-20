from pydantic import EmailStr, ConfigDict, BaseModel

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    description: str
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    description: str

    model_config = ConfigDict(from_attributes=True)