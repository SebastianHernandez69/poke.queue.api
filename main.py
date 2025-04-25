import uvicorn
import json
from fastapi import FastAPI
from utils.db import execute_query_json
from controllers.PokeRequestController import insert_poke_request, update_poke_request, get_poke_request, get_all_request
from models.PokeRequest import PokeRequest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/")
async def root():
    query = "select * from pokequeue.MESSAGES"
    result = await execute_query_json(query)
    result_dict = json.loads(result)
    return result_dict

@app.get("/version")
async def version():
    return {"version": "0.2.0"}


@app.get("/api/request/{id}")
async def get_request(id: int):
    return await get_poke_request( id )

@app.get("/api/request")
async def select_all_request():
    return await get_all_request( )

@app.post("/api/request")
async def create_request(poke_request: PokeRequest):
    return await insert_poke_request( poke_request )

@app.put("/api/request")
async def update_request(poke_request: PokeRequest):
    return await update_poke_request( poke_request )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

