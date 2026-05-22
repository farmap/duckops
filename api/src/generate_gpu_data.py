import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import duckdb
import sqlite3
from app.config import basedir, rootdir
from app.utils import parent_dir

def generate_parquet():
    data_dir = os.path.join(rootdir,"data/raw")
    os.makedirs(data_dir, exist_ok=True)
    parquet_path = os.path.join(data_dir, "duckops-gpu-metrics.parquet")
    
    # Generate time series data: 1 week, every 1 hour
    now = datetime.now()
    times = [now - timedelta(hours=i) for i in range(24*7)][::-1]
    
    gpus = ['PRD.BGPU.A01', 'PRD.BGPU.A02', 'PRD.BGPU.B01', 'PRD.BGPU.B02']
    
    # Averages for each GPU (instances/hour)
    gpu_averages = {
        'PRD.BGPU.A01': 80.0,
        'PRD.BGPU.A02': 65.0,
        'PRD.BGPU.B01': 45.0,
        'PRD.BGPU.B02': 30.0
    }
    
    all_records = []
    
    for gpu in gpus:
        avg = gpu_averages[gpu]
        # Generate base values with standard deviation noise (around 8% of the average)
        values = np.random.normal(avg, avg * 0.08, len(times))
        
        # Randomly inject spikes: ~5 random indexes out of 168 (approx. every ~30 hours)
        # Spikes should be about 30% higher than the average for each series
        spike_indices = np.random.choice(len(times), size=5, replace=False)
        for idx in spike_indices:
            values[idx] = avg * 1.3 + np.random.normal(0, avg * 0.03)
            
        values = np.maximum(values, 0) # Ensure no negative values
        
        for t, val in zip(times, values):
            all_records.append({
                "timestamp": t,
                "gpu_name": gpu,
                "value": round(val, 2)
            })
            
    df = pd.DataFrame(all_records)
    
    # Use duckdb to copy dataframe to parquet
    duckdb.sql("COPY df TO '{}' (FORMAT PARQUET)".format(parquet_path))
    print(f"Created Parquet file at {parquet_path}")
    return parquet_path

def update_db(parquet_path):
    # Direct SQLite connection to avoid hanging on metadata or engine initialization
    db_path = os.path.join(parent_dir(basedir), "instance/db.sqlite3")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, skipping update.")
        return
        
    try:
        # Connect to SQLite with a short 3.0 second timeout to prevent indefinite hangs
        conn = sqlite3.connect(db_path, timeout=3.0)
        cursor = conn.cursor()
        
        # Update the existing demo post so it seamlessly points to the new GPU Parquet file
        cursor.execute("UPDATE posts SET data_path = ? WHERE slug = ?", (parquet_path, "bgpu-metrics"))
        conn.commit()
        if cursor.rowcount > 0:
            print("Successfully updated database post 'bgpu-metrics' to use GPU metrics.")
        else:
            print("Post 'bgpu-metrics' not found in database.")
        conn.close()
    except Exception as e:
        print(f"Database update skipped or failed: {e}")

if __name__ == "__main__":
    path = generate_parquet()
    update_db(path)
