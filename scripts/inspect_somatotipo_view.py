from sqlalchemy import inspect, text

from src.backend.database import engine


VIEW_NAME = "CDRVistaValoracionCorporal"


def main():
    inspector = inspect(engine)
    tables_and_views = set(inspector.get_table_names()) | set(inspector.get_view_names())
    if VIEW_NAME not in tables_and_views:
        print(f"No se encontro {VIEW_NAME}.")
        return

    print(f"Columnas de {VIEW_NAME}:")
    for column in inspector.get_columns(VIEW_NAME):
        print(f"- {column['name']} ({column['type']})")

    with engine.connect() as connection:
        try:
            result = connection.execute(text(f"SHOW CREATE VIEW {VIEW_NAME}"))
            row = result.fetchone()
        except Exception as error:
            print(f"No se pudo obtener SHOW CREATE VIEW: {error}")
            return

    if row:
        print("")
        print("Definicion SQL de la vista:")
        print(row[-1])


if __name__ == "__main__":
    main()
