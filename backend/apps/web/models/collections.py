from pydantic import BaseModel
from peewee import *
from playhouse.shortcuts import model_to_dict
from typing import List, Union, Optional
import time
import logging
import uuid
from apps.web.internal.db import DB
import json
import os
from config import SRC_LOG_LEVELS, UPLOAD_DIR

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Documents DB Schema
####################


class Collection(Model):
    name = CharField()
    key = CharField(unique=True)
    title = CharField()
    content = TextField(null=True)
    user_id = CharField()
    timestamp = DateField()

    class Meta:
        database = DB


class CollectionModel(BaseModel):
    name: str
    key: str
    title: str
    content: Optional[str] = None
    user_id: str
    timestamp: int  # timestamp in epoch


####################
# Forms
####################


class CollectionResponse(BaseModel):
    name: str
    title: str
    key: str
    content: Optional[str] = None
    user_id: str
    timestamp: int  # timestamp in epoch


class CollectionUpdateForm(BaseModel):
    name: str
    title: str
    content: Optional[str] = None


class CollectionForm(CollectionUpdateForm):
    content: Optional[str] = None


class CollectionTable:
    def __init__(self, db):
        self.db = db
        self.db.create_tables([Collection])


    def insert_new_collection(
        self, user_id: str, form_data: CollectionForm
    ) -> Optional[CollectionModel]:
        
        collection = CollectionModel(
            **{
                **form_data.model_dump(),
                "user_id": user_id,
                "key": str(uuid.uuid4()),
                "timestamp": int(time.time()),
            }
        )
        try:
            result = Collection.create(**collection.model_dump())
            if result:
                return collection
            else:
                return None
        except:
            return None

    def get_collection_by_name(self, name: str) -> Optional[CollectionModel]:
        try:
            collection = Collection.get(Collection.name == name)
            return CollectionModel(**model_to_dict(collection))
        except:
            return None
        
    def get_collection_by_key(self, key: str) -> Optional[CollectionModel]:
        try:
            collection = Collection.get(Collection.key == key)
            return CollectionModel(**model_to_dict(collection))
        except:
            return None

    def get_collections(self) -> List[CollectionModel]:
        return [
            CollectionModel(**model_to_dict(collection))
            for collection in Collection.select()
            # .limit(limit).offset(skip)
        ]

    def update_collection_by_name(
        self, name: str, form_data: CollectionUpdateForm
    ) -> Optional[CollectionModel]:
        try:
            query = Collection.update(
                name=form_data.name,
                timestamp=int(time.time()),
            ).where(Collection.name == name)
            query.execute()

            doc = Collection.get(Collection.name == form_data.name)
            return CollectionModel(**model_to_dict(doc))
        except Exception as e:
            log.exception(e)
            return None
    
    def update_collection_by_key(
        self, key: str, form_data: CollectionUpdateForm
    ) -> Optional[CollectionModel]:
        try:
            query = Collection.update(
                 **form_data.model_dump(),
                timestamp=int(time.time()),
            ).where(Collection.key == key)
            query.execute()

            collection = Collection.get(Collection.key == key)
            return CollectionModel(**model_to_dict(collection))
        except Exception as e:
            log.exception(e)
            return None

    def update_doc_content_by_name(
        self, name: str, updated: dict
    ) -> Optional[CollectionModel]:
        try:
            collection = self.get_doc_by_name(name)
            collection_content = json.loads(collection.content if collection.content else "{}")
            collection_content = {**collection_content, **updated}

            query = Collection.update(
                content=json.dumps(collection_content),
                timestamp=int(time.time()),
            ).where(Collection.name == name)
            query.execute()

            collection = Collection.get(Collection.name == name)
            return CollectionModel(**model_to_dict(collection))
        except Exception as e:
            log.exception(e)
            return None

    def delete_doc_by_name(self, name: str) -> bool:
        try:
            query = Collection.delete().where((Collection.name == name))
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False
        
    def delete_doc_by_key(self, key: str) -> bool:
        try:
            query = Collection.delete().where((Collection.key == key))
            query.execute()  # Remove the rows, return number of rows removed.

            return True
        except:
            return False


Collections = CollectionTable(DB)


def build_collection_file_contents(original_filename: str, collection: str = None):
    path = create_collection_directory(collection)
    unsanitized_filename = str(uuid.uuid4()) + '_' + original_filename.replace(" ", "_")
    filename = os.path.basename(unsanitized_filename)
    file_path = f"{path}/{filename}"
    return {
        "file_path":file_path, 
        "filename":filename, 
        "path": path, 
        "collection": collection, 
        "original_filename": original_filename
    }


def get_collection_from_path(path: str) -> None:
        split = path.split("/")
        collection = split[len(split) - 2]
        return collection
        
def create_collection_directory(collection: str = None) -> None:
        directory_base = collection if collection else "default"
        directory = f"{UPLOAD_DIR}/{directory_base}"
        try:
           os.makedirs(directory, exist_ok=True)
        except:
            pass
        return directory

def build_collections_as_dict(collections: List[str]) -> List[dict]:
    return json.loads(json.dumps([{
            "collection_names": collections,
            "type": "collection"
        }]))
    
def build_collections_as_json(collections: List[dict]) -> json:
    return json.loads(json.dumps(collections))