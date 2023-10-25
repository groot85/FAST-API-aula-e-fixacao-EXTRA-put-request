from pydantic import BaseModel
from uuid import UUID, uuid4  #gerar id automatico e aleatorio
from typing import Optional, List  #preenchimento randomica opcional
from enum import Enum  #para trab com perfil|role


class Role(str, Enum):
	role_1 = "admin"
	role_2 = "aluna"
	role_3 = "instrutora"


#propriedades
class UserBase(BaseModel):
	id: Optional[UUID] = uuid4()
	first_name: Optional[str]
	last_name: Optional[str]
	email: Optional[str]
	role: Optional[List[Role]]


class UserCreate(UserBase):
	pass


class UserUpdate(UserBase):
	pass
