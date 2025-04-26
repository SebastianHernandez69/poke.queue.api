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
        query = "EXEC pokequeue.sp_create_poke_request ?, ? "
        params = (poke_request.pokemon_type, poke_request.sample_size,) 
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


async def delete_pokemon_report(report_id: int):
    try:
        query_check = "SELECT * FROM pokequeue.requests WHERE id = ?"
        params = (report_id,)
        exists = await execute_query_json(query_check, params)
        if not json.loads(exists):
            raise HTTPException(status_code=404, detail="Reporte no encontrado")

        blob = AzBlob()
        try:
            blob.delete_blob(report_id)
        except Exception as e:
            logger.warning(f"No se pudo eliminar el blob del reporte {report_id}: {e}")

        query_delete = "DELETE FROM pokequeue.requests WHERE id = ?"
        
        await execute_query_json(query_delete, params, True)

        return {"message": f"Reporte {report_id} eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar el reporte {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar el reporte")