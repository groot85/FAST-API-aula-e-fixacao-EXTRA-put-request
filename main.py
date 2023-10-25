#atividade das aulas 4 sobre APIexercicio FAST API extra put request

from fastapi import FastAPI, HTTPException
from uuid import UUID  #gerar id automatico e aleatorio
from typing import List  #para importar minha classe ede lista que está no models
from models import UserBase, UserCreate, UserUpdate, Role

#material para regras de doc: https://docs.github.com/pt/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

app = FastAPI()

db: List[UserBase] = [
 UserCreate(id=UUID("9e870356-0878-49a8-b3c3-4ca58e4bc91f"),
            first_name="Ana",
            last_name="Avila",
            email="ana@gmail.com",
            role=[Role.role_1]),
 UserCreate(id=UUID("756ea772-6360-4594-b833-094297db7e55"),
            first_name="Laura",
            last_name="Queiroz",
            email="laura@gmail.com",
            role=[Role.role_2]),
 UserCreate(id=UUID("478d6b25-83b7-4f8e-affd-9893f0a94d37"),
            first_name="Cesar",
            last_name="Rezende",
            email="laura@gmail.com",
            role=[Role.role_3]),
]

@app.get("/")
async def root():
	return {"message": "Ei, Ana! Finalmente deu certo, né?"}

@app.get("/api/users")
async def get_users():
	return db

@app.get("/api/users/{id}")
async def get_user(id: UUID):
	for user in db:
		if user.id == id:
			return user
	return {"message": "Usuário não está aqui!"}

@app.put("/api/users/{id}")
async def get_user(id: UUID, user_update: UserUpdate):
	for index, user in enumerate(db):
		if user.id == id:
			db[index] = user_update
			return user_update
	return {"message": "Usuário não encontrado!"}

@app.post("/api/users")
async def create_user(user: UserCreate):
	"""
	Adicionar um usuário na nossa base de dados:
	- **id**: UUID
	- **first_name**: string
	- **last_name**: string
	- **email**: string
	- **role**: Role
	"""
	db.append(user)
	return user

@app.delete("/api/users/{id}")
async def delete_user(id: UUID):
	for user in db:
		if user.id == id:
			db.remove(user)
			return
	raise HTTPException(status_code=404,
	                    detail=f"Usuário com id {id} não está aqui!")
