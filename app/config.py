import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY',
                           'default_secret_key')  # Используйте переменную окружения или значение по умолчанию
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        'sqlite:///board.db')  # Используйте переменную окружения или значение по умолчанию
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY',
                               'default_jwt_secret_key')  # Используйте переменную окружения или значение по умолчанию
