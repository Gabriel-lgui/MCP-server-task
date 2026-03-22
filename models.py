from pydantic import EmailStr, ConfigDict, BaseModel

class UserCreate(BaseModel): # Usado para criar um novo usuário (EmailStr é usado para validação de email)
    
    name: str
    email: EmailStr
    description: str
    
class UserReturn(BaseModel): # Usado para retornar informações do usuário 
    
    id: int
    name: str
    email: EmailStr
    description: str

    model_config = ConfigDict(from_attributes=True)
    