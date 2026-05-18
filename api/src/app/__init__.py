import duckdb
from fastapi import FastAPI, Depends, HTTPException
from app.services.db_services import get_db
from sqlalchemy.orm import Session
from app.config import settings
from typing import List, Optional
from uuid import UUID

from app.services.db_services import get_db

from app.schemas.post import PostGet, PostCreate, PostUpdate
from app.schemas.metric import MetricResponse

from app.models.post import Post


def create_app() -> FastAPI:
    app = FastAPI(title='DuckOps - DevOps Blog and Data API',
                version='1.0.0',
                debug=settings.FASTAPI_DEBUG)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get('/config/user', response_model=None)
    def get_config_user() -> None:
        """
        Retrieve list of all users
        """
        return []

    @app.get('/metrics/{post_slug}', response_model=MetricResponse)
    def get_metrics_post_slug(post_slug: str, db: Session = Depends(get_db)) -> MetricResponse:
        """
        Get data for a specific blog post
        """
        post = Post.get_by_name(db, post_slug, unique_field="slug")
        if not post or not post.data_path:
            raise HTTPException(status_code=404, detail="Metrics not found")
        
        try:
            query = f"SELECT timestamp, value FROM read_parquet('{post.data_path}') ORDER BY timestamp"
            df = duckdb.query(query).df()
            
            return MetricResponse(
                labels=df['timestamp'].astype(str).tolist(),
                datasets=[
                    {"label": "Process Lag", "data": df['value'].tolist(), "unit": "ms"}
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

    @app.get('/posts', tags=["posts"], response_model=List[PostGet])
    def get_posts(db: Session = Depends(get_db), ) -> List[PostGet]:
        """
        List all posts
        """
        all_posts = Post.get_all(db)
        return all_posts

    @app.post('/posts', response_model=None, responses={'201': {'model': PostGet}})
    def post_posts(body: PostCreate, db: Session = Depends(get_db), ) -> Optional[PostGet]:
        """
        Create a new post
        """
        Post.create(db, **body.model_dump())
        created_db = Post.get_by_name(db,body.slug,unique_field="slug")
        return created_db

    @app.get('/posts/{id}', response_model=PostGet)
    def get_posts_id(id: UUID, db: Session = Depends(get_db)) -> PostGet:
        """
        Get a post by UUID
        """
        post = Post.get_by_id(db, id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    @app.put('/posts/{id}', response_model=None)
    def put_posts_id(id: UUID, body: PostUpdate, db: Session = Depends(get_db)) -> None:
        """
        Update a post
        """
        post = Post.get_by_id(db, id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        post.update(db, **body.model_dump(exclude_unset=True))

    @app.delete('/posts/{id}', response_model=None)
    def delete_posts_id(id: UUID, db: Session = Depends(get_db)) -> None:
        """
        Delete a post
        """
        post = Post.get_by_id(db, id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        post.delete(db)

    return app