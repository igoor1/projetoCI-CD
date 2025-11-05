from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title= "YourDisc")

class Album(BaseModel):
    nome: str
    artista: str
    ano: str

albums = {
    1: {"nome": "Nectar", "Artista": "Joji", "ano": "2020"},
    2: {"nome": "Wait On Me - The 4th Mini Album", "Artista": "Kai", "ano": "2025"},
    3: {"nome": "SYRE", "Artista": "Jaden", "ano": "2017"},
    4: {"nome": "Pretty", "Artista": "Artemas", "ano": "2024"},
    5: {"nome": "White Poney", "Artista": "Deftones", "ano": "2000"}
}


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/albums")
async def get_all():
    return albums


@app.get("/albums/{album_id}")
async def get_album(album_id: int):
    if album_id not in albums:
        raise HTTPException(status_code=404, detail="Album não encontrado")
    return albums[album_id]

@app.post("/albums")
async def create_album(album: Album):
    global albums
    novo_id = max(albums.keys()) + 1 
    albums[novo_id] = album.model_dump()
    return {"id": novo_id, **album.model_dump()}


@app.put("/albums/{album_id}")
async def update_album(album_id: int, album: Album):
    global albums
    if album_id not in albums:
        raise HTTPException(status_code=404, detail="Album não encontrado")
    albums[album_id] = album.model_dump()
    return {"id": album_id, **album.model_dump()}


@app.delete("/albums/{album_id}")
async def delete_album(album_id: int):
    global albums
    if album_id not in albums:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    del albums[album_id]
    return {"message": "Album deletado com sucesso"}
    