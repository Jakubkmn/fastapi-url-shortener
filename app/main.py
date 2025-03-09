from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from uuid import uuid4
from base62 import encode

# SQLite database configuration
sqlite_file_name = 'database.session'
sqlite_url = f'sqlite:///{sqlite_file_name}'
connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    """Dependency for getting database session."""
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

class URLShortener(SQLModel, table=True):
    """
    Model representing a shortened URL entry.

    Attributes:
        id (int): Primary key.
        original_url (str): The original long URL.
        shorten_url (str): The generated short URL.
        click_count (int): The number of times the short URL has been accessed.
    """
    id: int | None = Field(default=None, primary_key=True)
    original_url: str = Field(index=True)
    shorten_url: str = Field(index=True, unique=True)
    click_count: int = Field(default=0)

    def generate_short_code(self, session: SessionDep):
        """Generate a short code using UUID4 and base62 encoding"""
        uuid_code = uuid4().int
        self.shorten_url = encode(uuid_code)[:7]
        session.add(self)
        session.commit()
        session.refresh(self)
        return self.shorten_url
    
    @classmethod
    def lookup_url(cls, session: SessionDep, short_code: str):
        """Find original URL by short code and increment click counter"""
        statement = select(cls).where(cls.shorten_url == short_code)
        result = session.exec(statement).first()

        if result is None:
            return 0

        result.click_count += 1
        session.add(result)
        session.commit()
        session.refresh(result)
        return result.original_url
    

class ShortenRequest(BaseModel):
    """Validation schema for URL shortening request"""
    original_url: str

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get('/', include_in_schema=False)
async def root():
    return RedirectResponse(url='/docs')

@app.post("/shorten/")
async def shorten_url(request: ShortenRequest, session: SessionDep):
    """
    Endpoint to shorten a URL.

    Args:
        request (ShortenRequest): Contains the original URL.
        session (SessionDep): Database session.

    Returns:
        dict: A dictionary containing the original URL and the generated short URL.
    """
    url = URLShortener(original_url=request.original_url)
    short_code = url.generate_short_code(session)
    return {'original_url': request.original_url, 'shorten_url': short_code}

@app.get('/{short_code}')
async def redirect(short_code: str, session: SessionDep):
    """
    Redirects a short URL to its original URL.

    Args: 
        short_code (str): The short code of the URL.
        session (SessionDep): Database session.

    Returns:
        RedirectResponse: Redirects the user to the original URL

    Raises:
        HTTPException: 404 error if the short code is not found.
    """
    original_url = URLShortener.lookup_url(session, short_code)
    if original_url:
        return RedirectResponse(url=original_url)
    raise HTTPException(status_code=404, detail="URL not found")

@app.get('/stats/')
async def get_all_rows(session: SessionDep):
    """
    Retrieves all URL records from the database.

    Args:
        session (SessionDep): Database session.

    Returns:
        dict: JSON-encoded list of all stored URLs and their statistics.
    """
    result = session.exec(select(URLShortener)).all()
    return jsonable_encoder({'stats': result})

@app.get("/stats/{short_code}")
async def get_stats(short_code: str, session: SessionDep):
    """
    Retrieves statistics for a specific short URL.

    Args:
        short_code (str): The short code of the URL.
        session (SessionDep): Database session.

    Returns:
        dict: JSON-encoded statistics including original URL and click count.
    
    Raises:
        HTTPException: 404 error if the short code is not found.
    """
    result = session.exec(select(URLShortener).where(URLShortener.shorten_url == short_code)).first()
    if result is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return jsonable_encoder({"stats": result})