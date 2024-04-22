from fastapi import Depends, FastAPI, HTTPException, status, responses
from datetime import datetime, timedelta
from typing import List, Union, Optional

from fastapi import APIRouter

from pydantic import BaseModel
import json

from apps.web.models.documents import (
    Documents,
    DocumentForm,
    DocumentUpdateForm,
    DocumentResponse,
)

from utils.utils import get_current_user, get_admin_user
from constants import ERROR_MESSAGES


router = APIRouter()


@router.get('/download/{collection}')
async def download_docs(collection: str, user=Depends(get_current_user)):
    doc = Documents.get_docs_by_collection_name(collection)
    if doc and len(doc) > 0:
       document = doc[0]
       file_path = Documents.get_file_location(document)
       file_name = document.original_filename if document.original_filename else document.filename
       return responses.FileResponse(path=file_path, filename=file_name, media_type='application/octet-stream')
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.COLLECTION_DOCUMENTS_EXISTS,
        )

############################
# GetDocsWithFilenames 
############################
@router.get('/files/', response_model=List[DocumentResponse])
async def get_docs_with_filenames(filenames: str, user=Depends(get_current_user)):
    parsedFileNames = json.loads(filenames) 
    documents = Documents.get_docs_by_filename(parsedFileNames)
    return [
         DocumentResponse(
            **{
                **doc.model_dump(),
                "content": json.loads(doc.content if doc.content else "{}"),
            }
        )
        for doc in documents
    ]
############################
# GetDocuments
############################


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(collection: str = None, user=Depends(get_current_user)):
    docs = [
        DocumentResponse(
            **{
                **doc.model_dump(),
                "content": json.loads(doc.content if doc.content else "{}"),
            }
        )
        for doc in (Documents.get_docs_by_collection(collection=collection) if collection else Documents.get_docs())
    ]
    return docs


############################
# CreateNewDoc
############################


@router.post("/create", response_model=Optional[DocumentResponse])
async def create_new_doc(form_data: DocumentForm, user=Depends(get_admin_user)):
    doc = Documents.get_doc_by_name(form_data.name)
    if doc == None:
        doc = Documents.insert_new_doc(user.id, form_data)

        if doc:
            return DocumentResponse(
                **{
                    **doc.model_dump(),
                    "content": json.loads(doc.content if doc.content else "{}"),
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.FILE_EXISTS,
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.NAME_TAG_TAKEN,
        )


############################
# GetDocByName
############################


@router.get("/name/{name}", response_model=Optional[DocumentResponse])
async def get_doc_by_name(name: str, user=Depends(get_current_user)):
    doc = Documents.get_doc_by_name(name)
    if doc:
        return DocumentResponse(
            **{
                **doc.model_dump(),
                "content": json.loads(doc.content if doc.content else "{}"),
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

############################
# GetDocsByCollection
############################

@router.post("/collection/{collection}", response_model=Optional[DocumentResponse])
async def get_docs_by_collection(collection: str, user=Depends(get_current_user)):
    doc = Documents.get_docs_by_collection(collection)
    if doc:
        return DocumentResponse(
            **{
                **doc.model_dump(),
                "content": json.loads(doc.content if doc.content else "{}"),
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.COLLECTION_DOCUMENTS_EXISTS,
        )
        
############################
# TagDocByName
############################


class TagItem(BaseModel):
    name: str


class TagDocumentForm(BaseModel):
    name: str
    tags: List[dict]


@router.post("/name/{name}/tags", response_model=Optional[DocumentResponse])
async def tag_doc_by_name(form_data: TagDocumentForm, user=Depends(get_current_user)):
    doc = Documents.update_doc_content_by_name(form_data.name, {"tags": form_data.tags})

    if doc:
        return DocumentResponse(
            **{
                **doc.model_dump(),
                "content": json.loads(doc.content if doc.content else "{}"),
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateDocByName
############################


@router.post("/name/{name}/update", response_model=Optional[DocumentResponse])
async def update_doc_by_name(
    name: str, form_data: DocumentUpdateForm, user=Depends(get_admin_user)
):
    doc = Documents.update_doc_by_name(name, form_data)
    if doc:
        return DocumentResponse(
            **{
                **doc.model_dump(),
                "content": json.loads(doc.content if doc.content else "{}"),
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


@router.delete("/name/{name}/delete", response_model=bool)
async def delete_doc_by_name(name: str, user=Depends(get_admin_user)):
    result = Documents.delete_doc_by_name(name)
    return result


@router.delete("/delete", response_model=bool)
async def delete_doc_by_name(user=Depends(get_admin_user)):
    result = Documents.delete_all_docs()
    return result
