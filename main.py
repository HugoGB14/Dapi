import socket
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import os
import datetime
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

filesDirectory = './download'

def format_file_details(path: str) -> Dict[str, str]:
    stats = os.stat(path)
    return {
        "size": stats.st_size,
        "last_modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "last_accessed": datetime.datetime.fromtimestamp(stats.st_atime).isoformat(),
        "created": datetime.datetime.fromtimestamp(stats.st_ctime).isoformat()
    }


@app.post("/mkdir")
def makeDir(route: str = Form(...), name: str = Form(...)):
    os.makedirs(os.path.join(filesDirectory, route, name), exist_ok=True)
    return {"message": 'Created sucssesfully'}

@app.post("/upload")
def upload_file(route: str = Form(...), file: UploadFile = File(...)):
    directory_path = os.path.join(filesDirectory, route)
    os.makedirs(directory_path, exist_ok=True)
    
    file_path = os.path.join(directory_path, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "message": "Uploaded successfully"}

@app.get("/list")
def list_directory(route: str = ""):
    directory_path = os.path.join(filesDirectory, route)
    
    if not os.path.exists(directory_path):
        return {"error": "Directory does not exist"}
    
    try:
        items = os.listdir(directory_path)
        result = []
        for item in items:
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                result.append({"name": item, "type": "directory"})
            elif os.path.isfile(item_path):
                result.append({"name": item, "type": "file"})
            else:
                result.append({"name": item, "type": "unknown"})
        
        return {"items": result}
    except Exception as e:
        return {"error": str(e)}
    
    
@app.get("/download")
def download_file(filename: str, route: str = ""):
    file_path = os.path.join(filesDirectory, route, filename)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')

@app.delete("/delete/file")
def delete_file(filename: str, route: str = ""):
    file_path = os.path.join(filesDirectory, route, filename)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/directory")
def delete_directory(route: str):
    directory_path = os.path.join(filesDirectory, route)
    
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise HTTPException(status_code=404, detail="Directory not found")
    
    try:
        shutil.rmtree(directory_path)
        return {"message": "Directory deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/file/details/")
def get_file_details(filename: str, route: str = ""):
    file_path = os.path.join(filesDirectory, route, filename)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_details = format_file_details(file_path)
    file_details["path"] = file_path
    file_details["type"] = "file"
    return file_details

@app.get("/directory/details/")
def get_directory_details(route: str):
    # Construir la ruta completa del directorio
    directory_path = os.path.join(filesDirectory, route)
    
    # Verificar si el directorio existe
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise HTTPException(status_code=404, detail="Directory not found")
    
    # Obtener detalles del directorio
    stats = os.stat(directory_path)
    directory_details = {
        "size": stats.st_size,
        "last_modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "last_accessed": datetime.datetime.fromtimestamp(stats.st_atime).isoformat(),
        "created": datetime.datetime.fromtimestamp(stats.st_ctime).isoformat(),
        "path": directory_path,
        "type": "directory"
    }
    
    return directory_details    