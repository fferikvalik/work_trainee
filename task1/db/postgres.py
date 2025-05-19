import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresDB:
    def __init__(self, env_path: str = ".env"):
        load_dotenv(env_path)
        self.host = os.getenv("PGHOST")
        self.port = os.getenv("PGPORT")
        self.dbname = os.getenv("PGDATABASE")
        self.user = os.getenv("PGUSER")
        self.password = os.getenv("PGPASSWORD")
        self._conn = None

    def connect(self):
        if not self._conn or self._conn.closed:
            self._conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )

    def close(self):
        if self._conn and not self._conn.closed:
            self._conn.close()

    def execute(self, query: str, params=None, fetch=False):
        self.connect()
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            self._conn.commit()