import duckdb
import os

class DBClient:
  def __init__(self):
        self.conn = duckdb.connect()
        self._load_data()

  def _load_data(self):
    folder_path = os.path.join("src", "db", "data")
    csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    for file in csv_files:
        table_name = os.path.splitext(file)[0]
        file_path = os.path.join(folder_path, file)
        self.conn.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path}')
        """)

  def execute_query(self, query: str, params: tuple):
      try:
          return self.conn.execute(query, params).df()
      except Exception as e:
          raise ValueError(f"Query failed: {e}")

