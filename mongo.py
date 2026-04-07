from pymongo import MongoClient
from flask import current_app


def init_mongo(app):
    try:
        mongo_uri = app.config.get("MONGO_URI")
        mongo_db_name = app.config.get("MONGO_DB_NAME")

        if not mongo_uri:
            raise RuntimeError("MONGO_URI no está configurado.")
        if not mongo_db_name:
            raise RuntimeError("MONGO_DB_NAME no está configurado.")

        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

        # Probar conexión real
        client.admin.command("ping")

        app.extensions["mongo_client"] = client
        app.extensions["mongo_db"] = client[mongo_db_name]

        print(f"MONGO OK -> URI: {mongo_uri} | DB: {mongo_db_name}")

    except Exception as e:
        app.extensions["mongo_client"] = None
        app.extensions["mongo_db"] = None
        print("ERROR INIT MONGO:", e)


def get_mongo_db():
    db = current_app.extensions.get("mongo_db")
    if db is None:
        raise RuntimeError("MongoDB no fue inicializado correctamente.")
    return db


def close_mongo(exception=None):
    # Si usas un cliente global en app.extensions, normalmente no lo cierres por request.
    pass