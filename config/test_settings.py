class Config:
    DEBUG = True
    # https://www.sqlite.org/inmemorydb.html
    # Sqlite in-memory databases cannot be accessed from multiple threads
    # SQLURI = "sqlite://"
    SQLURI = "sqlite:///db.sqlite3"
