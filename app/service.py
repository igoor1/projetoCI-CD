from . import database, model

db = database.db_albums

def get_album(album_id: int) -> model.Album | None:
    if album_id in db:
        album_data = db[album_id]
        return model.Album(id=album_id, **album_data)
    return None

def get_all() -> list[model.Album]:
    return [model.Album(id=key, **value) for key, value in db.items()]

def create_album(album: model.AlbumCreate) -> model.Album:
    novo_id = max(db.keys() or [0]) + 1
    album_data = album.model_dump()
    db[novo_id] = album_data
    return model.Album(id=novo_id, **album_data)

def update_album(album_id: int, album: model.AlbumCreate) -> model.Album | None:
    if album_id not in db:
        return None
    album_data = album.model_dump()
    db[album_id] = album_data
    return model.Album(id=album_id, **album_data)

def delete_album(album_id: int) -> bool:
    if album_id not in db:
        return False
    del db[album_id]
    return True