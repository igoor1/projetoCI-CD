from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from . import service, model

app = FastAPI(title= "YourDisc")

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/albums", response_model=list[model.Album])
async def get_all():
    return service.get_all()


@app.get("/albums/{album_id}", response_model=model.Album)
async def get_album(album_id: int):
    album = service.get_album(album_id=album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album não encontrado")
    return album


@app.post("/albums", response_model=model.Album, status_code=status.HTTP_201_CREATED)
async def create_album(album: model.AlbumCreate):
    return service.create_album(album=album)


@app.put("/albums/{album_id}", response_model=model.Album)
async def update_album(album_id: int, album: model.AlbumCreate):
    updated_album = service.update_album(album_id=album_id, album=album)
    if not updated_album:
        raise HTTPException(status_code=404, detail="Album não encontrado")
    return updated_album


@app.delete("/albums/{album_id}")
async def delete_album(album_id: int):
    success = service.delete_album(album_id)
    if not success:
        raise HTTPException(status_code=404, detail="Album não encontrado")
    return {"message": "Album deletado com sucesso"}
    