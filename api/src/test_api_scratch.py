from fastapi.testclient import TestClient
from app.__init__ import create_app
from app.services.db_services import Base, engine

# Create the tables in the test sqlite database
Base.metadata.create_all(bind=engine)

app = create_app()
client = TestClient(app)

def run_tests():
    # 1. Create a post
    response = client.post("/posts", json={
        "slug": "test-post",
        "title": "Test Post",
        "content": "This is a test post",
        "data_path": "/tmp/test.parquet"
    })
    print("CREATE POST:", response.status_code, response.json())
    assert response.status_code == 201 
    post_id = response.json()["id"]

    # 2. Get the post
    response = client.get(f"/posts/{post_id}")
    print("GET POST:", response.status_code, response.json())
    assert response.status_code == 200

    # 3. Update the post
    response = client.put(f"/posts/{post_id}", json={
        "title": "Updated Test Post",
        "slug": "test-post-updated",
        "content": "Updated content"
    })
    print("UPDATE POST:", response.status_code, response.json())
    assert response.status_code == 200

    # 4. Get the updated post
    response = client.get(f"/posts/{post_id}")
    print("GET UPDATED POST:", response.status_code, response.json())
    assert response.json()["title"] == "Updated Test Post"
    
    # 5. Delete the post
    response = client.delete(f"/posts/{post_id}")
    print("DELETE POST:", response.status_code)
    assert response.status_code == 204

    # 6. Get deleted post -> 404
    response = client.get(f"/posts/{post_id}")
    print("GET DELETED POST:", response.status_code, response.json())
    assert response.status_code == 404

    # 7. Check other endpoints
    response = client.get("/config/user")
    print("GET CONFIG USER:", response.status_code, response.json())

    response = client.get("/metrics/some-slug")
    print("GET METRICS:", response.status_code, response.json())

    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
