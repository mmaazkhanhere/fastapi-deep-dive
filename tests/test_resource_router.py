# tests/test_routers/test_resources.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

# Import dependencies and schemas from your application
from src.main import app
from src.backend.session import get_async_session
from src.backend.security import get_current_contributor_or_admin_user, get_current_admin_user
from src.schemas.user_schema import User, UserRole
from src.schemas.skills_schema import SkillCreate
from src.services.resource_service import LearningResourceService # To directly interact with service for setup/assertions
from src.schemas.learning_resource_schema import LearningResourceCreate, LearningResourceType


# --- Fixtures for Mocking Authentication Dependencies ---

# Define a mock user for contributor/admin roles
TEST_CONTRIBUTOR_USER = User(
    id=1,
    email="test_contributor@example.com",
    name="Man",
    is_active=True,
    password="hashed_password",
    role=UserRole.contributor
)

TEST_CONTRIBUTOR_USER = User(
    id=1,
    email="test_contributor@example.com",
    name="Man",
    is_active=True,
    password="hashed_password",
    role=UserRole.admin
)

@pytest.fixture
def mock_contributor_user():
    """Fixture that provides a mock contributor user."""
    return TEST_CONTRIBUTOR_USER


@pytest.fixture
def override_contributor_admin_dependency(mock_contributor_user):
    """Overrides get_current_contributor_or_admin_user to return a mock contributor."""
    app.dependency_overrides[get_current_contributor_or_admin_user] = lambda: mock_contributor_user
    yield
    app.dependency_overrides.pop(get_current_contributor_or_admin_user, None)

@pytest.fixture
def override_admin_dependency(mock_admin_user):
    """Overrides get_current_admin_user to return a mock admin."""
    app.dependency_overrides[get_current_admin_user] = lambda: mock_admin_user
    yield
    app.dependency_overrides.pop(get_current_admin_user, None)


# --- Test Cases ---

@pytest.mark.asyncio
async def test_get_fastapi_status(client: AsyncClient):
    """Test the basic /status endpoint."""
    response = await client.get("/status")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Status": "FastAPI Service Running"}


@pytest.mark.asyncio
async def test_get_all_resources_empty(client: AsyncClient):
    """Test getting all resources when none exist."""
    response = await client.get("/resources/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_resource_success(client: AsyncClient, session: AsyncSession, override_contributor_admin_dependency):
    """Test successful creation of a learning resource."""
    resource_data = {
        "title": "New Article",
        "description": "A great article on FastAPI testing.",
        "url": "http://example.com/new-article",
        "resource_type": "article",
        "difficulty": 3
    }
    response = await client.post("/resources/create", json=resource_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Learning Resource Created", "status": 201}

    # Verify resource is in DB
    service = LearningResourceService(session)
    resources_in_db = await service.get_all_resources()
    assert len(resources_in_db) == 1
    assert resources_in_db[0].title == "New Article"

    # Test cache invalidation: A subsequent GET /resources/ should reflect the new resource
    response_get = await client.get("/resources/")
    assert response_get.status_code == status.HTTP_200_OK
    assert len(response_get.json()) == 1
    assert response_get.json()[0]["title"] == "New Article" # Ensure new resource is returned

@pytest.mark.asyncio
async def test_create_resource_unauthorized(client: AsyncClient):
    """Test creating a resource without authentication."""
    resource_data = {
        "title": "Unauthorized Article",
        "description": "Should not be created.",
        "url": "http://example.com/unauth",
        "resource_type": "article",
        "difficulty": 1
    }
    response = await client.post("/resources/create", json=resource_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED # Assuming 401 for missing token


@pytest.mark.asyncio
async def test_get_resource_by_id_success(client: AsyncClient, session: AsyncSession, override_contributor_admin_dependency):
    """Test retrieving a resource by its ID."""
    # First, create a resource to fetch
    service = LearningResourceService(session)
    created_resource = await service.create_new_resource(
        LearningResourceCreate(
            title="Specific Resource",
            description="Details",
            url="http://example.com/specific",
            resource_type=LearningResourceType.video,
            difficulty=4
        )
    )
    resource_id = created_resource.id

    response = await client.get(f"/resources/{resource_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Specific Resource"
    assert response.json()["id"] == resource_id

    # Test caching: make another request, it should be served from cache
    # (You'd need to mock DB queries or check Redis directly to be 100% sure in unit tests,
    # but the speed difference or lack of DB logs would indicate it in integration tests)
    response_cached = await client.get(f"/resources/{resource_id}")
    assert response_cached.status_code == status.HTTP_200_OK
    assert response_cached.json()["title"] == "Specific Resource"


@pytest.mark.asyncio
async def test_get_resource_by_id_not_found(client: AsyncClient, override_contributor_admin_dependency):
    """Test retrieving a non-existent resource."""
    response = await client.get("/resources/99999") # Assuming 99999 does not exist
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Resource not found"


@pytest.mark.asyncio
async def test_update_resource_success(client: AsyncClient, session: AsyncSession, override_contributor_admin_dependency):
    """Test successful update of a resource."""
    service = LearningResourceService(session)
    original_resource = await service.create_new_resource(
        LearningResourceCreate(
            title="Original Title",
            description="Original Description",
            url="http://example.com/original",
            resource_type=LearningResourceType.book,
            difficulty=2
        )
    )
    resource_id = original_resource.id

    updated_data = {
        "title": "Updated Title",
        "description": "New Description",
        "url": "http://example.com/updated",
        "resource_type": "course", # Enum value
        "difficulty": 5
    }
    response = await client.put(f"/resources/{resource_id}/update", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Title"
    assert response.json()["description"] == "New Description"

    # Verify update in DB
    retrieved_resource = await service.get_resource_by_resource_id(resource_id)
    assert retrieved_resource.title == "Updated Title"

    # Test cache invalidation: GET /resources/ and specific ID should reflect update
    response_get_all = await client.get("/resources/")
    assert response_get_all.json()[0]["title"] == "Updated Title"
    response_get_id = await client.get(f"/resources/{resource_id}")
    assert response_get_id.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_resource_success(client: AsyncClient, session: AsyncSession, override_contributor_admin_dependency):
    """Test successful deletion of a resource."""
    service = LearningResourceService(session)
    resource_to_delete = await service.create_new_resource(
        LearningResourceCreate(
            title="Resource to Delete",
            description="Will be gone",
            url="http://example.com/delete",
            resource_type=LearningResourceType.article,
            difficulty=1
        )
    )
    resource_id = resource_to_delete.id

    response = await client.delete(f"/resources/{resource_id}/delete")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Learning Resource Deleted", "status": 200}

    # Verify deletion from DB
    deleted_resource = await service.get_resource_by_resource_id(resource_id)
    assert deleted_resource is None

    # Test cache invalidation: GET /resources/ should not return the deleted resource
    response_get_all = await client.get("/resources/")
    assert len(response_get_all.json()) == 0


@pytest.mark.asyncio
async def test_delete_admin_resource_success(client: AsyncClient, session: AsyncSession, override_admin_dependency):
    """Test successful deletion of a resource by an admin user."""
    service = LearningResourceService(session)
    resource_to_delete = await service.create_new_resource(
        LearningResourceCreate(
            title="Admin Delete Target",
            description="Only admins can delete",
            url="http://example.com/admindelete",
            resource_type=LearningResourceType.video,
            difficulty=5
        )
    )
    resource_id = resource_to_delete.id

    response = await client.delete(f"/resources/{resource_id}/admin/delete")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Learning Resource Deleted", "status": 200}

    # Verify deletion from DB
    deleted_resource = await service.get_resource_by_resource_id(resource_id)
    assert deleted_resource is None

@pytest.mark.asyncio
async def test_delete_admin_resource_forbidden(client: AsyncClient, session: AsyncSession, override_contributor_admin_dependency):
    """Test deletion by a non-admin user (should be forbidden)."""
    service = LearningResourceService(session)
    resource_to_keep = await service.create_new_resource(
        LearningResourceCreate(
            title="Should Not Be Deleted",
            description="Only admins can delete this one",
            url="http://example.com/keep",
            resource_type=LearningResourceType.book,
            difficulty=3
        )
    )
    resource_id = resource_to_keep.id

    response = await client.delete(f"/resources/{resource_id}/admin/delete")
    assert response.status_code == status.HTTP_403_FORBIDDEN # Assuming 403 for insufficient permissions


@pytest.mark.asyncio
async def test_add_skill_to_resource_success(client: AsyncClient, session: AsyncSession, override_contributor_admin_dependency):
    """Test adding a skill to a resource."""
    service = LearningResourceService(session)
    resource = await service.create_new_resource(
        LearningResourceCreate(
            title="Resource for Skills",
            description="Testing skills",
            url="http://example.com/skills",
            resource_type=LearningResourceType.course,
            difficulty=3
        )
    )
    resource_id = resource.id
    user_id = TEST_CONTRIBUTOR_USER.id # Using the ID of the mock user

    skill_data = {"name": "Python Testing", "description": "Skill in Pytest"}
    response = await client.post(f"/resources/{resource_id}/skills/{user_id}", json=skill_data) # Note the {user_id} in path based on your router
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Skill added to resource successfully"
    assert response.json()["skill"]["name"] == "Python Testing"

    # Verify in DB (you'd need to extend your service/models to fetch skills by resource)
    # For now, just check that it returns something.
    # If the service returns the actual skill object, you could fetch and verify.


@pytest.mark.asyncio
async def test_delete_skill_from_resource_success(client: AsyncClient, session: AsyncSession, override_contributor_admin_dependency):
    """Test deleting a skill from a resource."""
    # First, create a resource and add a skill to it (mimicking prior success)
    service = LearningResourceService(session)
    resource = await service.create_new_resource(
        LearningResourceCreate(
            title="Resource to delete skill from",
            description="Has skill",
            url="http://example.com/delete_skill",
            resource_type=LearningResourceType.book,
            difficulty=3
        )
    )
    resource_id = resource.id
    user_id = TEST_CONTRIBUTOR_USER.id

    skill_data = SkillCreate(title="ToBeDeleted")
    # This call to service.learning_resource_skill might return the actual skill object
    # which is needed to get the skill_id for the DELETE test.
    added_skill_response = await service.learning_resource_skill(resource_id, user_id, skill_data)
    skill_id = added_skill_response.id # Assuming it returns an object with an ID


    response = await client.delete(f"/resources/{resource_id}/skills/{user_id}/delete?skill_id={skill_id}") # Adjusted based on router signature
    assert response.status_code == status.HTTP_200_OK
    # Further assertions can be made on the response or by checking the database


@pytest.mark.asyncio
async def test_log_view_success(client: AsyncClient):
    """Test logging a resource view."""
    # For background tasks, we mostly test that the endpoint returns 200 OK
    # and the task is added. Verifying the task itself would involve mocking
    # the background task dispatcher or the log_resource_view function.
    resource_id = 1
    user_id = TEST_CONTRIBUTOR_USER.id # Example user ID
    response = await client.post(f"/resources/{resource_id}/log_view", params={"user_id": user_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "View logged"}

    # More advanced testing would involve mocking `src.tasks.log_resource_view`
    # to assert it was called with correct arguments.
    # from unittest.mock import patch
    # with patch('src.tasks.log_resource_view') as mock_log_view:
    #    response = await client.post(f"/resources/{resource_id}/log_view", params={"user_id": user_id})
    #    mock_log_view.assert_called_once_with(resource_id, user_id)


@pytest.mark.asyncio
async def test_upload_resource_image_success(client: AsyncClient, session: AsyncSession):
    """Test successful image upload."""
    # Create a dummy resource first
    service = LearningResourceService(session)
    resource = await service.create_new_resource(
        LearningResourceCreate(
            title="Image Target",
            description="For image upload",
            url="http://example.com/image_upload",
            resource_type=LearningResourceType.article,
            difficulty=3
        )
    )
    resource_id = resource.id

    # Create a dummy image file for upload
    image_content = b"fake image data"
    files = {"image_file": ("test_image.png", image_content, "image/png")}

    response = await client.post(f"/resources/{resource_id}/upload_image", files=files)
    assert response.status_code == status.HTTP_200_OK
    assert "Image uploaded successfully" in response.json()["message"]
    assert "image_url" in response.json()
    assert response.json()["content_type"] == "image/png"

    # Verify the file was actually written to the static directory (optional, but good for full integration)
    from pathlib import Path
    image_url = response.json()["image_url"]
    file_path_in_static = Path("static") / Path(image_url).relative_to("/static")
    assert file_path_in_static.exists()
    assert file_path_in_static.read_bytes() == image_content

    # Clean up the created file
    if file_path_in_static.exists():
        file_path_in_static.unlink()


@pytest.mark.asyncio
async def test_upload_resource_image_invalid_type(client: AsyncClient, session: AsyncSession):
    """Test uploading a non-image file."""
    # Create a dummy resource
    service = LearningResourceService(session)
    resource = await service.create_new_resource(
        LearningResourceCreate(
            title="Bad Image Target",
            description="For invalid image upload",
            url="http://example.com/bad_image",
            resource_type=LearningResourceType.article,
            difficulty=3
        )
    )
    resource_id = resource.id

    # Create a dummy text file
    file_content = b"this is not an image"
    files = {"image_file": ("test.txt", file_content, "text/plain")}

    response = await client.post(f"/resources/{resource_id}/upload_image", files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Only image files are allowed."