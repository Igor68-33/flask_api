import logging

from dotenv import load_dotenv
from flask import Flask

from .extensions import db, bcrypt, jwt

# Загружаем переменные окружения из файла .env
load_dotenv()


def create_app():
    app = Flask(__name__)

    # Конфигурация приложения
    app.config.from_object('app.config.Config')  # Загрузка конфигурации
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений

    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Инициализация расширений extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Регистрация блюпринтов
    from app.routers import api  # Импортируем блюпринт
    app.register_blueprint(api)

    with app.app_context():
        from app import models
        db.create_all()  # Создание таблиц

    # Обработка ошибок
    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"404 Error: {error}")
        return {"message": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Error: {error}")
        return {"message": "Internal server error"}, 500

    return app
