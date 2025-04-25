import json
import logging

from fastapi import HTTPException
from models.PokeRequest import PokeRequest
from utils.db import execute_query_json
from utils.AzQueue import AzQueue
from utils.AzBlob import AzBlob

#logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_poke_request(id: int) -> dict:
    try:
        query = "SELECT * FROM pokequeue.requests WHERE ID = ?"
        params = (id,) 
        result = await execute_query_json( query, params )
        result_dict = json.loads(result)
        
        return result_dict
    except Exception as e:
        logger.error(f"Error getting poke request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
async def update_poke_request(poke_request: PokeRequest) -> dict:
    try:
        query = "EXEC pokequeue.sp_update_poke_request ?, ?, ?"
        params = (poke_request.id, poke_request.status, poke_request.url or "",) 
        result = await execute_query_json( query, params, True )
        result_dict = json.loads(result)
        
        return result_dict
    except Exception as e:
        logger.error(f"Error updating poke request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
async def insert_poke_request(poke_request: PokeRequest) -> dict:
    try:
        query = "EXEC pokequeue.sp_create_poke_request ? "
        params = (poke_request.pokemon_type,) 
        result = await execute_query_json( query, params, True )
        result_dict = json.loads(result)
        
        await AzQueue().insert_message_on_queue( result )

        return result_dict
    except Exception as e:
        logger.error(f"Error inserting poke request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

async def get_all_request() -> dict:
    query = """
        select 
            r.id as ReportId
            , s.description as Status
            , r.type as PokemonType
            , r.url 
            , r.created 
            , r.updated
        from pokequeue.requests r 
        inner join pokequeue.status s 
        on r.id_status = s.id 
    """
    result = await execute_query_json( query  )
    result_dict = json.loads(result)
    blob = AzBlob()
    for record in result_dict:
        id = record['ReportId']
        record['url'] = f"{record['url']}?{blob.generate_sas(id)}"
    return result_dict