"""Temp File Handle."""

from datetime import datetime

import pytz

from OSIx.models.local_db_models import TempDataOrmEntity
from OSIx.database.local_db import LOCAL_DB_INSTANCE


class TempFileHandler:
    """Temporary File Hander."""

    @staticmethod
    def file_exist(path: str) -> bool:
        """
        Return if a File Exists.

        :param path: File Path
        :return:
        """

        return bool(LOCAL_DB_INSTANCE.local_db_session.query(TempDataOrmEntity).filter_by(path=path).count() > 0)

    @staticmethod
    def read_file_text(path: str) -> str:
        """
        Read All File Content.

        :param path: File Path
        :return: File Content
        """

        entity: TempDataOrmEntity = LOCAL_DB_INSTANCE.local_db_session.query(TempDataOrmEntity).filter_by(path=path).first()
        return str(entity.data)

    @staticmethod
    def remove_expired_entries() -> int:
        """Remove all Expired Entries."""

        total: int = LOCAL_DB_INSTANCE.local_db_session.execute(
            TempDataOrmEntity.__table__.delete().where(
                TempDataOrmEntity.valid_at <= int(datetime.now(tz=pytz.UTC).timestamp())
                )
            ).rowcount

        LOCAL_DB_INSTANCE.local_db_session.flush()
        LOCAL_DB_INSTANCE.local_db_session.commit()
        return total

    @staticmethod
    def purge() -> int:
        """Remove all Entries."""

        total: int = LOCAL_DB_INSTANCE.local_db_session.execute(TempDataOrmEntity.__table__.delete()).rowcount
        LOCAL_DB_INSTANCE.local_db_session.flush()
        LOCAL_DB_INSTANCE.local_db_session.commit()
        return total

    @staticmethod
    def write_file_text(path: str, content: str, validate_seconds: int = 3600) -> None:
        """
        Write Text Content into File.

        :param path: File Path
        :param content: File Content
        :param validate_seconds: File Validation in Seconds
        :return: None
        """

        # Delete if Exists
        LOCAL_DB_INSTANCE.local_db_session.execute(
            TempDataOrmEntity.__table__.delete().where(TempDataOrmEntity.path == path)
            )

        entity: TempDataOrmEntity = TempDataOrmEntity(
            path=path,
            data=content,
            created_at=int(datetime.now(tz=pytz.UTC).timestamp()),
            valid_at=int(datetime.now(tz=pytz.UTC).timestamp()) + validate_seconds
            )
        LOCAL_DB_INSTANCE.local_db_session.add(entity)

        # Execute
        LOCAL_DB_INSTANCE.local_db_session.flush()
        LOCAL_DB_INSTANCE.local_db_session.commit()
