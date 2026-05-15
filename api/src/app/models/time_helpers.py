from sqlalchemy import TypeDecorator, DateTime
import datetime

class UTCDateTime(TypeDecorator):
    """
    Forces SQLite datetime objects to be timezone-aware UTC.
    """
    impl = DateTime
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None:
            # If the datetime is naive, attach UTC info
            if value.tzinfo is None:
                return value.replace(tzinfo=datetime.timezone.utc)
        return value