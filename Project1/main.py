from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

# Uvicorn is the web server we use to start a FastAPI application
app = FastAPI()

class Book(BaseModel):
    title : str = Field(..., title = "Title of the book")
    author : str = Field(..., title = "Author of the book")
    genre : str = Field(..., title = "Genre of the book")

BOOKS = [
    {
        "Title" : "Mindset: The New Psychology of Success",
        "Author" : "Carol Dweck",
        "Genre" : "Self-help book"
    },
    {
        "Title" : "Siddhartha",
        "Author" : "Hermann Hesse",
        "Genre" : "Novel, Fiction"
    },
    {
        "Title" : "Demian",
        "Author" : "Hermann Hesse",
        "Genre" : "Novel, Fiction, Künstlerroman"
    },
    {
        "Title" : "Steppenwolf",
        "Author" : "Hermann Hesse",
        "Genre" : "Novel, Autobiography, Existential Fiction"
    },
    {
        "Title" : "Ikigai: The Japanese Secret to a Long and Happy Life",
        "Author" : "Hector Garcia, Francesc Miralles",
        "Genre" : "Self-help book"
    },
    {
        "Title" : "The Psychology of Money: Timeless Lessons on Wealth, Greed, and Happiness",
        "Author" : "Morgan Housel",
        "Genre" : "Self-help book"
    },
    {
        "Title" : "Atomic Habits",
        "Author" : "James Clear",
        "Genre" : "Self-help book"
    },
    {
        "Title" : "The Kaiju Preservation Society",
        "Author" : "John Scalzi",
        "Genre" : "Science fiction"
    },
]

@app.get("/books/")
async def read_all_books(author_name : Optional[str] = Query(None, description = "Author of the book"), 
                         book_title : Optional[str] = Query(None, description = "Title of the book")):
    try:
        filtered_books = BOOKS
        if author_name:
            filtered_books = [book for book in filtered_books if book["Author"].upper() == author_name.upper()]

            if not filtered_books:
                return {"message" : f"No books found for author '{author_name}'"}
        
        if book_title:
            filtered_books = [book for book in filtered_books if book["Title"].upper() == book_title.upper()]
            
            if not filtered_books:
                return {"message " : f"Author - {author_name} has not written any book with title - {book_title}"}
        
        if len(filtered_books) == 1:
            return filtered_books[0]
        elif filtered_books:
            return filtered_books
        else:
            return {"message" : "No books found matching the criteria"}
    except Exception as e :
        return {"message" : f"An unexpected error occurred : {e}"}


@app.get("/books/title/{book_title}/")
async def generate_book_title(book_title : str):
    try:
        book_with_title = [book for book in BOOKS if book["Title"].upper() == book_title.upper()]

        if not book_with_title:
            return {"message" : f"No books found with title '{book_title}'"}
        else:
            return book_with_title[0]
    except Exception as e :
        return {"message" : f"An unexpected error occurred : {e}"}


@app.get("/books/author/{author_name}/")
async def generate_author_books(author_name : str):
    try:
        author_books = [book for book in BOOKS if book["Author"].upper() == author_name.upper()]

        if not author_books:
            return {"message" : f"No books found for author '{author_name}'"}

        if len(author_books) == 1:
            return author_books[0]
        else:
            return author_books
    except Exception as e :
        return {"message" : f"An unexpected error occurred : {e}"}


@app.post("/books/create_book/")
async def add_book(Title : str = Query(..., description = "Title of the book"), 
                   Author : str = Query(..., description = "Author of the book"), 
                   Genre : str = Query(..., description = "Genre of the book")):
    try:
        book = {"Title" : Title, "Author" : Author, "Genre" : Genre}
        BOOKS.append(book)
        return {"message" : "Book added successfully", "book" : book}
    except Exception as e :
        return {"message" : f"An unexpected error occurred : {e}"}


@app.put("/books/update_book/")
async def update_book(Title : str = Query(..., description = "Title of the book"), 
                   Author : str = Query(..., description = "Author of the book"), 
                   Genre : str = Query(..., description = "Genre of the book")):
    try:
        for i in BOOKS:
            if i["Title"].upper() == Title.upper():
                i["Author"] = Author
                i["Genre"] = Genre
                book = {"Title" : Title, "Author" : Author, "Genre" : Genre}
                return {"message" : "Book updated successfully", "book" : book}
        else:
            return {"message" : f"No books found with title '{Title}'"}
    except Exception as e :
        return {"message" : f"An unexpected error occurred : {e}"}


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title : str):
    try:
        for i in BOOKS:
            if i["Title"].upper() == book_title.upper():
                BOOKS.remove(i)
                return {"message" : "Book deleted successfully"}
        else:
            return {"message" : f"No books found with title '{book_title}'"}
    except Exception as e :
        return {"message" : f"An unexpected error occurred : {e}"}
