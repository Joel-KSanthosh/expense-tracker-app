from dependency_injector import containers, providers

from backend.app.database import Database
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.user_service import UserService


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Dependency()

    user_repository = providers.Factory(
        provides=UserRepository,
        session=session,
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    repositories = providers.Container(Repositories, config=config)

    user = providers.Factory(
        provides=UserService,
        user_repo=repositories.user_repository,
    )


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres = providers.Singleton(
        provides=Database,
        dsn=config.postgres.dsn,
        min_size=config.postgres.min_size,
        max_size=config.postgres.max_size,
        echo=config.postgres.echo,
    )

    services = providers.Container(Services, config=config)
