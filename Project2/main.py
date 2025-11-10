from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Query, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status

# Uvicorn is the web server we use to start a FastAPI application
app = FastAPI()

current_year = datetime.now().year

class Book_Request_Body(BaseModel):
    id : Optional[int] = Field(default = None, description = "Book Id which will be auto-generated when we process this in a Database")
    title : str = Field(..., min_length = 3, max_length = 200, description = "Title of the book")
    book_description : str = Field(..., min_length = 3, max_length = 500, description = "Book description and a brief info. about")
    author : str = Field(..., min_length = 3, max_length = 100, description = "Author of the book")
    published_year : int = Field(..., gt = 1000, lt = current_year + 1, description = "Year of publication of the book")
    genre : str = Field(..., min_length = 3, max_length = 50, description = "Genre of the book")
    rating : int = Field(..., gt = 0, le = 5, description = "Rating of the book on scale 0-5")
    
    model_config = {
        "json_schema_extra" : {
            "example" : {
                "title" : "Vagabond",
                "book_description" : "Vagabond is a Japanese epic martial arts manga series written and illustrated by Takehiko Inoue. It portrays a fictionalized account of the life of Japanese swordsman Musashi Miyamoto, based on Eiji Yoshikawa's novel Musashi.",
                "author" : "Takehiko Inoue",
                "published_year" : 1998,
                "genre" : "Seinen manga, Jidaigeki",
                "rating" : 5
            }
        }
    }


class Book_Update_Request_Body(BaseModel):
    id : int = Field(..., ge = 0, description = "Book Id to which details should be updated")
    title : str = Field(..., min_length = 3, max_length = 200, description = "Title of the book")
    book_description : str = Field(..., min_length = 3, max_length = 500, description = "Book description and a brief info. about")
    author : str = Field(..., min_length = 3, max_length = 100, description = "Author of the book")
    published_year : int = Field(..., gt = 1000, lt = current_year + 1, description = "Year of publication of the book")
    genre : str = Field(..., min_length = 3, max_length = 50, description = "Genre of the book")
    rating : int = Field(..., gt = 0, le = 5, description = "Rating of the book on scale 0-5")
    
    model_config = {
        "json_schema_extra" : {
            "example" : {
                "id" : 5,
                "title" : "Vagabond",
                "book_description" : "Vagabond is a Japanese epic martial arts manga series written and illustrated by Takehiko Inoue. It portrays a fictionalized account of the life of Japanese swordsman Musashi Miyamoto, based on Eiji Yoshikawa's novel Musashi.",
                "author" : "Takehiko Inoue",
                "published_year" : 1998,
                "genre" : "Seinen manga, Jidaigeki",
                "rating" : 5
            }
        }
    }


class Book:
    def __init__(self, id, title, book_description, author, published_year, genre, rating):
        self.id = id
        self.title = title
        self.book_description = book_description
        self.author = author
        self.published_year = published_year
        self.genre = genre
        self.rating = rating


BOOKS = [
    Book(0, "Mindset: The New Psychology of Success", "Description0", "Carol S. Dweck", 2006, "Self-help book", 4), 
    Book(1, "Siddhartha", "Description1", "Hermann Hesse", 1922, "Novel, Fiction", 3), 
    Book(2, "Demian", "Description2", "Hermann Hesse", 1919, "Novel, Fiction, Künstlerroman", 3), 
    Book(3, "Steppenwolf", "Description3", "Hermann Hesse", 1927, "Novel, Autobiography, Existential Fiction", 3), 
    Book(4, "Ikigai: The Japanese Secret to a Long and Happy Life", "Description4", "Hector Garcia, Francesc Miralles", 2016, "Self-help book", 4), 
    Book(5, "The Psychology of Money: Timeless Lessons on Wealth, Greed, and Happiness", "Description5", "Morgan Housel", 2020, "Self-help book", 4), 
    Book(6, "Atomic Habits", "Description6", "James Clear", 2018, "Self-help book", 5), 
    Book(7, "The Kaiju Preservation Society", "Description7", "John Scalzi", 2022, "Science fiction", 3), 
]


def generate_book_id(book_obj):
    if BOOKS:
        last_book_id = BOOKS[-1].id
        new_book_id = last_book_id + 1
    else:
        new_book_id = 0
    book_obj.id = new_book_id
    return book_obj


@app.get("/books/", status_code = status.HTTP_200_OK)
async def read_all_books(author_name : Optional[str] = Query(None, description = "Author of the book"), 
                         book_title : Optional[str] = Query(None, description = "Title of the book"),
                         book_rating : Optional[int] = Query(None, gt = 0, le = 5, description = "Rating of the book"),
                         published_year : Optional[int] = Query(None, gt = 1000, lt = current_year + 1, description = "Year of first release of the book")):
    if not BOOKS:
        raise HTTPException(status_code = 404, detail = "No books present in the Database")
    
    filtered_books = BOOKS
    if author_name:
        filtered_books = [book for book in filtered_books if book.author.upper() == author_name.upper()]
        
        if not filtered_books:
            raise HTTPException(status_code = 404, detail = f"No books found for author - {author_name}")
    
    if book_title:
        filtered_books = [book for book in filtered_books if book.title.upper() == book_title.upper()]
        
        if not filtered_books:
            raise HTTPException(status_code = 404, detail = f"No book found with title - {book_title}")
    
    if book_rating:
        filtered_books = [book for book in filtered_books if book.rating == book_rating]
        
        if not filtered_books:
            raise HTTPException(status_code = 404, detail = f"No book found with rating - {book_rating}")
    
    if published_year:
        filtered_books = [book for book in filtered_books if book.published_year == published_year]
        
        if not filtered_books:
            raise HTTPException(status_code = 404, detail = f"No book found with published year - {published_year}")
        
    if len(filtered_books) == 1:
        return filtered_books[0]
    elif filtered_books:
        return filtered_books
    else:
        raise HTTPException(status_code = 404, detail = "No books found matching the criteria")


@app.get("/books/title/{book_title}/", status_code = status.HTTP_200_OK)
async def generate_book_title(book_title : str = Path(min_length = 3, max_length = 200, description = "Title of the book")):
    if not BOOKS:
        raise HTTPException(status_code = 404, detail = "No books present in the Database")
    
    book_with_title = [book for book in BOOKS if book.title.upper() == book_title.upper()]
    
    if not book_with_title:
        raise HTTPException(status_code = 404, detail = f"No book found with title - {book_title}")
    
    return book_with_title[0]


@app.get("/books/{book_id}/", status_code = status.HTTP_200_OK)
async def get_book_based_on_book_id(book_id : int = Path(ge = 0, description = "Book ID of the book")):
    if not BOOKS:
        raise HTTPException(status_code = 404, detail = "No books present in the Database")
    
    book_based_on_book_id = [book for book in BOOKS if book.id == book_id]
    
    if not book_based_on_book_id:
        raise HTTPException(status_code = 404, detail = f"No book found with ID - '{book_id}'")
    
    return book_based_on_book_id[0]


@app.get("/books/author/{author_name}/", status_code = status.HTTP_200_OK)
async def generate_author_books(author_name : str = Path(min_length = 3, max_length = 100, description = "Author of the book")):
    if not BOOKS:
        raise HTTPException(status_code = 404, detail = "No books present in the Database")
    
    author_books = [book for book in BOOKS if book.author.upper() == author_name.upper()]
    
    if not author_books:
        raise HTTPException(status_code = 404, detail = f"No books found for author - {author_name}")
    
    if len(author_books) == 1:
        return author_books[0]
    
    return author_books


@app.post("/books/", status_code = status.HTTP_201_CREATED)
async def add_book(payload_request : Book_Request_Body):
    new_book = Book(**payload_request.model_dump())
    new_book = generate_book_id(new_book)
    BOOKS.append(new_book)
    return {"message" : "Book added successfully", "book" : new_book}


@app.put("/books/", status_code = status.HTTP_204_NO_CONTENT)
async def update_book(payload_request : Book_Update_Request_Body):
    if not BOOKS:
        raise HTTPException(status_code = 404, detail = "No books present in the Database")
    
    for idx, book in enumerate(BOOKS):
        if book.id == payload_request.id:
            BOOKS[idx] = Book(**payload_request.model_dump())
            print(f"Updated list - {BOOKS}")
            return {"message" : "Book updated successfully", "book" : BOOKS[idx]}
    raise HTTPException(status_code = 404, detail = f"No book found with ID - {payload_request.id}")


@app.delete("/books/{book_id}", status_code = status.HTTP_200_OK)
async def delete_book(book_id : int = Path(ge = 0, description = "Book ID of the book")):
    if not BOOKS:
        raise HTTPException(status_code = 404, detail = "No books present in the Database")
    
    for book in BOOKS:
        if book.id == book_id:
            BOOKS.remove(book)
            return {"message" : "Book deleted successfully"}
    raise HTTPException(status_code = 404, detail = f"No book found with ID - {book_id}")













# PRACTICE CODES
# @app.put("/books/update_book/")
# async def update_book(Title : str = Query(..., description = "Title of the book"), 
#                    Author : str = Query(..., description = "Author of the book"), 
#                    Genre : str = Query(..., description = "Genre of the book")):
#     try:
#         for book in BOOKS:
#             if book.title.upper() == Title.upper():
#                 book.author = Author
#                 book.genre = Genre
#                 return {"message" : "Book updated successfully", "book" : book}
#         else:
#             return {"message" : f"No books found with title '{Title}'"}
#     except Exception as e :
#         return {"message" : f"An unexpected error occurred : {e}"}