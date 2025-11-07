from pydantic import BaseModel

class AlbumBase(BaseModel):
    nome: str
    artista: str
    ano: str

class AlbumCreate(AlbumBase):
    pass

class Album(BaseModel):
    id: int
    nome: str
    artista: str
    ano: str

    class Config:
        from_attributes = True