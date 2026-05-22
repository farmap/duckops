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
from app.schemas.user import UserResponse, UserCreate, UserUpdate

from app.models.post import Post
from app.models.user import User
from app.services.blog_mdx import generate_blog_mdx, delete_blog_mdx


def create_app() -> FastAPI:
    app = FastAPI(title='DuckOps - DevOps Blog and Data API',
                version='1.0.0',
                debug=settings.FASTAPI_DEBUG)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get('/config/user', tags=["users"], response_model=List[UserResponse])
    def get_users(db: Session = Depends(get_db)) -> List[UserResponse]:
        """
        Retrieve list of all users
        """
        return User.get_all(db)

    @app.post('/config/user', tags=["users"], response_model=UserResponse, status_code=201)
    def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
        """
        Create a new user
        """
        return User.create(db, **user.model_dump())

    @app.get('/config/user/{id}', tags=["users"], response_model=UserResponse)
    def get_user_by_id(id: UUID, db: Session = Depends(get_db)) -> UserResponse:
        """
        Retrieve a user by ID
        """
        user = User.get_by_id(db, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @app.put('/config/user/{id}', tags=["users"], response_model=UserResponse)
    def update_user(id: UUID, user_update: UserUpdate, db: Session = Depends(get_db)) -> UserResponse:
        """
        Update a user
        """
        user = User.get_by_id(db, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_update.model_dump(exclude_unset=True)
        return User.update(db, id, **update_data)

    @app.delete('/config/user/{id}', tags=["users"], status_code=204)
    def delete_user(id: UUID, db: Session = Depends(get_db)) -> None:
        """
        Delete a user
        """
        user = User.get_by_id(db, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        User.delete(db, id)

    @app.get('/metrics/{post_slug}', response_model=MetricResponse)
    def get_metrics_post_slug(post_slug: str, db: Session = Depends(get_db)) -> MetricResponse:
        """
        Get data for a specific blog post
        """
        post = Post.get_by_name(db, post_slug, unique_field="slug")
        if not post or not post.data_path:
            raise HTTPException(status_code=404, detail="Metrics not found")
        
        try:
            # Check the columns in the parquet file
            rel = duckdb.read_parquet(post.data_path)
            columns = rel.columns
            
            if "gpu_name" in columns:
                query = f"SELECT timestamp, gpu_name, value FROM read_parquet('{post.data_path}') ORDER BY timestamp, gpu_name"
                df = duckdb.query(query).df()
                
                # Extract sorted list of unique timestamps as strings
                labels = sorted(df['timestamp'].astype(str).unique().tolist())
                
                datasets = []
                gpus = sorted(df['gpu_name'].unique().tolist())
                for gpu in gpus:
                    gpu_df = df[df['gpu_name'] == gpu].sort_values('timestamp')
                    datasets.append({
                        "label": gpu,
                        "data": gpu_df['value'].tolist(),
                        "unit": "instances/hour"
                    })
                
                return MetricResponse(labels=labels, datasets=datasets)
            elif "instance_count" in columns and "max_total" in columns:
                query = f"SELECT timestamp, instance_count, max_total FROM read_parquet('{post.data_path}') ORDER BY timestamp"
                df = duckdb.query(query).df()
                
                # Extract sorted list of unique timestamps as strings
                labels = sorted(df['timestamp'].astype(str).unique().tolist())
                
                datasets = []
                datasets.append({
                    "label": "Instance Count",
                    "data": df['instance_count'].tolist(),
                    "unit": "instances/minute"
                })
                datasets.append({
                    "label": "Max Run Time",
                    "data": df['max_total'].tolist(),
                    "unit": "seconds"
                })
                
                return MetricResponse(labels=labels, datasets=datasets)
            else:
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

    @app.post('/posts', response_model=PostGet, status_code=201)
    def post_posts(body: PostCreate, db: Session = Depends(get_db), ) -> Optional[PostGet]:
        """
        Create a new post
        """
        Post.create(db, **body.model_dump())
        created_db = Post.get_by_name(db,body.slug,unique_field="slug")
        if created_db:
            generate_blog_mdx(
                post_id=str(created_db.id),
                slug=created_db.slug,
                title=created_db.title,
                content=created_db.content,
                data_path=created_db.data_path
            )
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
        
        # Re-generate the MDX file with the updated values
        updated_post = Post.get_by_id(db, id)
        if updated_post:
            generate_blog_mdx(
                post_id=str(updated_post.id),
                slug=updated_post.slug,
                title=updated_post.title,
                content=updated_post.content,
                data_path=updated_post.data_path
            )

    @app.delete('/posts/{id}', response_model=None, status_code=204)
    def delete_posts_id(id: UUID, db: Session = Depends(get_db)) -> None:
        """
        Delete a post
        """
        post = Post.get_by_id(db, id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
            
        # Delete the MDX post from disk on database deletion
        delete_blog_mdx(post.slug)
        
        post.delete(db)

    return app