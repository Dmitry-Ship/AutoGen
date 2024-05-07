from typing_extensions import Annotated
from infra.postgres import PostgresManager
from dotenv import load_dotenv
import os

load_dotenv(override=True)

db_connection = PostgresManager()
db_connection.connect_with_url(os.getenv("DB_URI"))

def run_query(query: Annotated[str, "The sql query to run"]) -> Annotated[str, "The result of the query"]:
    return db_connection.run_sql(query)

def get_schema() -> Annotated[str, "The where schema of the database"]:
    return db_connection.get_table_definitions_for_prompt()