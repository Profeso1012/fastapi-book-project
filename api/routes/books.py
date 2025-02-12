from typing import OrderedDict

from fastapi import APIRouter, status

from fastapi.responses import JSONResponse

from api.db.schemas import Book, Genre, InMemoryDB

router = APIRouter()

db = InMemoryDB()
db.books = {
    1: Book(
        id=1,
        title="The Hobbit",
        author="J.R.R. Tolkien",
        publication_year=1937,
        genre=Genre.SCI_FI,
    ),
    2: Book(
        id=2,
        title="The Lord of the Rings",
        author="J.R.R. Tolkien",
        publication_year=1954,
        genre=Genre.FANTASY,
    ),
    3: Book(
        id=3,
        title="The Return of the King",
        author="J.R.R. Tolkien",
        publication_year=1955,
        genre=Genre.FANTASY,
    ),
}

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    db.add_book(book)
    return book, 201

@router.get(
    "/", response_model=OrderedDict[int, Book], status_code=status.HTTP_200_OK
)
async def get_books() -> OrderedDict[int, Book]:
    return db.get_books()

# ✅ FIXED: Ensure proper error handling for invalid book IDs
@router.get("/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def get_book(book_id: str):
    """Retrieve a book by its ID, handling invalid inputs correctly"""
    
    # ✅ Ensure the book_id is a valid integer
    if not book_id.isdigit():
        return JSONResponse(status_code=400, content={"detail": "Invalid book ID. Must be an integer."})
    
    book_id = int(book_id)
    if book_id not in db.books:
        return JSONResponse(status_code=404, content={"detail": "Book not found"})
    
    return db.books[book_id]

@router.put("/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book: Book) -> Book:
    updated_book = db.update_book(book_id, book)
    if updated_book is None:
        return {"detail": "Book not found"}, 404
    return updated_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int) -> None:
    if db.get_book(book_id) is None:
        return {"detail": "Book not found"}, 404
    db.delete_book(book_id)
    return {}, 204
