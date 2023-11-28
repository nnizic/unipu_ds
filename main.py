from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

#Model za upise
class Item(BaseModel):
    name:str
    description:str = None

#spremanje podataka u memoriju
items = []

#napravi upis (async)
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    items.append(item)
    return item

#Pročitaj sve upise (async)
@app.get("/items/", response_model=List[Item])
async def read_items():
    return items

#Pročitaj jedan unos prema ID (async)
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, details="Item not found")
    return items[item_id]

#Izmjeni unos
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status,code=404, detail="Item not found")
    items[item_id] = item
    return item

#Izbriši unos prema ID (async)
@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPExpection(status_code=404, details="Item not found")
    deleted_items = items.pop(item_id)
    return deleted_item
