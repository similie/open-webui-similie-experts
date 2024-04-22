from fastapi import Depends, FastAPI, HTTPException, status
from typing import List, Optional
from fastapi import APIRouter

import json

from apps.web.models.collections import (
    Collections,
    CollectionForm,
    CollectionResponse,
    CollectionUpdateForm,
)

from apps.web.models.documents import (
    DocumentResponse,
)


from utils.utils import get_current_user, get_admin_user
from constants import ERROR_MESSAGES

router = APIRouter()

############################
# GetCollections
############################


@router.get("/", response_model=List[CollectionResponse])
async def get_collections(user=Depends(get_current_user)):
    collections = [
        CollectionResponse(
            **{
                **collection.model_dump(),
            }
        )
        for collection in Collections.get_collections()
    ]
    return collections


############################
# CreateNewCollection
############################


@router.post("/create", response_model=Optional[CollectionResponse])
async def create_new_doc(form_data: CollectionForm, user=Depends(get_admin_user)):

        collection = Collections.insert_new_collection(user.id, form_data)

        if collection:
            return CollectionResponse(
                **{
                    **collection.model_dump(),
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.FILE_EXISTS,
            )
  


############################
# GetCollectionByKey
############################


@router.get("/{key}", response_model=Optional[CollectionResponse])
async def get_collection_by_name(key: str, user=Depends(get_current_user)):
    collection = Collections.get_collection_by_key(key)

    if collection:
        return CollectionResponse(
            **{
                **collection.model_dump(),
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# TagDocByName
############################


# class TagItem(BaseModel):
#     name: str


# class TagDocumentForm(BaseModel):
#     name: str
#     tags: List[dict]


# @router.post("/name/{name}/tags", response_model=Optional[DocumentResponse])
# async def tag_doc_by_name(form_data: TagDocumentForm, user=Depends(get_current_user)):
#     doc = Documents.update_doc_content_by_name(form_data.name, {"tags": form_data.tags})

#     if doc:
#         return DocumentResponse(
#             **{
#                 **doc.model_dump(),
#                 "content": json.loads(doc.content if doc.content else "{}"),
#             }
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=ERROR_MESSAGES.NOT_FOUND,
#         )



############################
# UpdateDocByName
############################


@router.put("/{key}", response_model=Optional[CollectionResponse])
async def update_collection_by_key(
    key: str, form_data: CollectionUpdateForm, user=Depends(get_admin_user)
):
    collection = Collections.update_collection_by_key(key, form_data)
    if collection:
        return CollectionResponse(
            **{
                **collection.model_dump(),
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NAME_TAG_TAKEN,
        )


############################
# DeleteDocByName
############################


@router.delete("/{key}", response_model=bool)
async def delete_collection_by_key(key: str, user=Depends(get_admin_user)):
    result = Collections.delete_doc_by_key(key)
    return result
