import os

from fastapi import FastAPI, HTTPException, Body, status
from fastapi.responses import Response
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from pydantic.functional_validators import BeforeValidator
from pymongo import ReturnDocument
from bson import ObjectId
import motor.motor_asyncio
from typing_extensions import Annotated


app = FastAPI()

# povezivanje sa bazom
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.fipu_baza
items_collection = db.get_collection("items")

# predstavlja ObjectId polje iz baze
# pokazuje se kao 'str' i meže se serijalizirati u json
PyObjectId = Annotated[str, BeforeValidator(str)]

# Model za upise
class ItemModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    description: str = Field(...)
    model_config = ConfigDict(
        populate_by_name = True,
        arbitrary_types_allowed=True,
        json_schema_extra = {
                "example": {
                    "name": "Pizza",
                    "description": "vrlo ukusno jelo"
                    }
                },
        )


class UpdateItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model_config = ConfigDict(
        populate_by_name = True,
        arbitrary_types_allowed=True,
        json_schema_extra = {
                "example": {
                    "name": "Pizza",
                    "description": "vrlo ukusno jelo"
                    }
                },
        )


class ItemCollection(BaseModel):
    """
    kontejner za instance ItemModel -a
    zbog sigurnosnih razloga
    """
    items: List[(ItemModel)]

#napravi upis (async)
@app.post(
        "/items/", 
        response_model=ItemModel,
        response_description="Dodaj novi item",
        status_code=status.HTTP_201_CREATED,
        response_model_by_alias=False,
        )
async def create_item(item: ItemModel = Body(...)):
    new_item = await items_collection.insert_one(
            item.model_dump(by_alias=True, exclude=["id"])
            )
    created_item = await items_collection.find_one(
            {"_id": new_item.inserted_id}
            )
    return created_item


#Pročitaj sve upise (async)
@app.get("/items/",
         response_description="Izlistaj sve iteme",
         response_model=ItemCollection,
         response_model_by_alias=False,
         )
async def read_items():
    return ItemCollection(items=await items_collection.find().to_list(1000))  

#Pročitaj jedan unos prema ID (async)
@app.get("/items/{id}",
         response_description="Izlistaj jedan item prema ID",
         response_model=ItemModel,
         response_model_by_alias=False,
         )

async def read_item(id: str):
    if (
            item := await items_collection.find_one({"_id": ObjectId(id)})
            ) is not None:
        return item
    raise HTTPException(status_code=404, detail=f"Item  {id} nije pronadjen")


# Izmjeni unos
@app.put("/items/{id}",
         response_description="Izmjeni podatke",
         response_model=ItemModel,
         response_model_by_alias=False,
         )
async def update_item(id: str, item: UpdateItem = Body(...)):
    item = {
            k: v for k, v in item.model_dump(by_alias=True).items() if v is not None
            }
    if len(item) >= 1:
        update_result = await items_collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": item},
                return_document=ReturnDocument.AFTER,
                )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Item  {id} nije pronadjen")
    # izmjena je prazna ali ipak treba vratiti item
    if (existing_item := await items_collection.find_one({"_id": id})) is not None:
        return existing_item

# Izbriši unos prema ID (async)
@app.delete("/items/{id}", response_description="Izbrisi item")
async def delete_item(id: str):
    delete_result = await items_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Item {id} nije pronadjen.")
