import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'tech_user'
    MYSQL_PASSWORD = 'StrongPassword123!'
    MYSQL_DB = 'tech_jobs_db'
    SECRET_KEY = os.urandom(24)
