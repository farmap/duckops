from app.services.db_services import Base, engine, SessionLocal
from app.models.post import Post

Base.metadata.create_all(bind=engine)
db = SessionLocal()

post = Post(
    slug="duckops-api-demo",
    title="DuckOps Interactive API Demo",
    content="This is the content stored in the API database.",
    data_path="/data/duckops-api-demo.parquet"
)
db.add(post)
db.commit()
db.refresh(post)
print(f"SEEDED POST UUID: {post.id}")
