import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.main import app
from src.db.database import Base, get_db
from src.core.cache import RedisCache, cache as app_cache
from src.core.config import get_settings

settings = get_settings()
TEST_DATABASE_URL = "postgresql+asyncpg://fraud_user:fraud_pass@localhost:5432/fraud_detection_test"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def test_db(test_engine):
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(scope="session")
async def test_redis():
    test_cache = RedisCache()
    await test_cache.connect()
    yield test_cache
    try:
        if test_cache.redis_client:
            await test_cache.redis_client.aclose()
    except Exception:
        pass

@pytest_asyncio.fixture
async def client(test_db, test_redis):
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Replace app cache with test cache client
    original_redis = app_cache.redis_client
    app_cache.redis_client = test_redis.redis_client
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Restore
    app_cache.redis_client = original_redis
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def redis_client(test_redis):
    yield test_redis

@pytest.fixture
def sample_transaction():
    return {
        "transaction_id": "TEST-001",
        "transaction": {
            "V1": -1.3598071336738,
            "V2": -0.0727811733098497,
            "V3": 2.53634673796914,
            "V4": 1.37815522427443,
            "V5": -0.338320769942518,
            "V6": 0.462387777762292,
            "V7": 0.239598554061257,
            "V8": 0.0986979012610507,
            "V9": 0.363786969611213,
            "V10": 0.0907941719789316,
            "V11": -0.551599533260813,
            "V12": -0.617800855762348,
            "V13": -0.991389847235408,
            "V14": -0.311169353699879,
            "V15": 1.46817697209427,
            "V16": -0.470400525259478,
            "V17": 0.207971241929242,
            "V18": 0.0257905801985591,
            "V19": 0.403992960255733,
            "V20": 0.251412098239705,
            "V21": -0.018306777944153,
            "V22": 0.277837575558899,
            "V23": -0.110473910188767,
            "V24": 0.0669280749146731,
            "V25": 0.128539358273528,
            "V26": -0.189114843888824,
            "V27": 0.133558376740387,
            "V28": -0.0210530534538215,
            "Time": 406,
            "Amount": 1.0
        }
    }

@pytest.fixture
def headers():
    return {"X-API-Key": settings.API_KEY}
