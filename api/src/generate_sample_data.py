import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import duckdb
from app.services.db_services import Base, engine, SessionLocal
from app.models.post import Post

def generate_parquet():
    os.makedirs("/home/farma/programming/projects/duckops/data/raw", exist_ok=True)
    parquet_path = "/home/farma/programming/projects/duckops/data/raw/duckops-api-demo.parquet"
    
    # Generate time series data: 1 week, every 1 hour
    now = datetime.now()
    times = [now - timedelta(hours=i) for i in range(24*7)][::-1]
    
    # Process Lag with some randomness and a spike
    base_lag = np.random.normal(50, 10, len(times)) # mean 50ms, std 10
    spike_start = int(len(times) * 0.7)
    base_lag[spike_start:spike_start+10] += np.random.normal(200, 50, 10) # Inject spike
    base_lag = np.maximum(base_lag, 10) # No negative lag
    
    df = pd.DataFrame({
        "timestamp": times,
        "value": base_lag.round(2)
    })
    
    # Use duckdb to copy dataframe to parquet
    duckdb.sql("COPY df TO '{}' (FORMAT PARQUET)".format(parquet_path))
    print(f"Created Parquet file at {parquet_path}")
    return parquet_path

def update_db(parquet_path):
    db = SessionLocal()
    post = db.query(Post).filter(Post.slug == "duckops-api-demo").first()
    if post:
        post.data_path = parquet_path
        db.commit()
        print("Updated Post in SQLite")
    else:
        print("Post not found!")
    db.close()

if __name__ == "__main__":
    path = generate_parquet()
    update_db(path)
