from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .database import get_db_connection, init_db
from . import main
import asyncio

app = FastAPI()

class Cours(BaseModel):
    theme: str

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/generer_cours/")
async def generer_cours(cours: Cours):
    theme = cours.theme
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO cours (theme, status) VALUES (?, ?)", (theme, "en_attente"))
    cours_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    # Lancer la génération du cours en arrière-plan
    asyncio.create_task(generer_cours_async(cours_id, theme))
    
    return {"id": cours_id, "theme": theme, "status": "en_attente"}

async def generer_cours_async(cours_id: int, theme: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE cours SET status = ? WHERE id = ?", ("en_cours", cours_id))
    conn.commit()
    conn.close()

    filepath = await main.main_async(theme)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE cours SET fichier_path = ?, status = ? WHERE id = ?", (filepath, "terminé", cours_id))
    conn.commit()
    conn.close()

@app.get("/cours/{cours_id}")
async def get_cours(cours_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cours WHERE id = ?", (cours_id,))
    cours = cur.fetchone()
    conn.close()
    
    if cours is None:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    
    result = {
    "id": cours['id'],
    "theme": cours['theme'],
    "status": cours['status'],
    "fichier_path": cours['fichier_path'] if cours['status'] == "terminé" else None
}
    
    if cours['status'] == "terminé" and cours['fichier_path']:
        with open(cours['fichier_path'], 'r', encoding='utf-8') as f:
            contenu = f.read()
        result["sommaire"] = cours['sommaire']
        result["contenu"] = contenu
    
    return result

@app.get("/cours")
async def list_cours():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, theme, status FROM cours")
    cours_list = cur.fetchall()
    conn.close()
    
    return [dict(cours) for cours in cours_list]