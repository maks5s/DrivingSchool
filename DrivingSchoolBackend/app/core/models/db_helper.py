from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config import settings


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        host: str,
        port: int,
        db_name: str,
        dbms_engine: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        self.host: str = host
        self.port: int = port
        self.db_name: str = db_name
        self.dbms_engine: str = dbms_engine
        self.echo: bool = echo
        self.echo_pool: bool = echo_pool
        self.pool_size: int = pool_size
        self.max_overflow: int = max_overflow

        self.engine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self):
        await self.engine.dispose()

    async def session_getter(self):
        async with self.session_factory() as session:
            yield session

    def _get_user_pwd_connection_string(
        self,
        username: str,
        password: str,
    ):
        return f"{self.dbms_engine}://{username}:{password}@{self.host}:{self.port}/{self.db_name}"

    # Dynamic session generator based on username and password conn string
    async def user_pwd_session_getter(
        self,
        username: str,
        password: str,
    ):
        engine = create_async_engine(
            url=self._get_user_pwd_connection_string(username, password),
            echo=self.echo,
            echo_pool=self.echo_pool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
        )
        session_factory = async_sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

        async with session_factory() as session:
            yield session


db_helper = DatabaseHelper(
    url=str(settings.db.url),
    host=settings.db.host,
    port=settings.db.port,
    db_name=settings.db.db_name,
    dbms_engine=settings.db.dbms_engine,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)
