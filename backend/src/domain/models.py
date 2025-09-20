from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    # used for alembic migrations and ORM
    pass


class CryptoPairName(Base):
    __tablename__ = "crypto_pairs_names"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crypto_name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    supported_exchanges: Mapped[list["SupportedExchangesByCrypto"]] = relationship(
        back_populates="crypto_names", cascade="all, delete"
    )


class SupportedExchangesByCrypto(Base):
    __tablename__ = "supported_exchanges_by_crypto"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crypto_id: Mapped[int] = mapped_column(ForeignKey("crypto_pairs_names.id"))
    supported_exchange: Mapped[str] = mapped_column(nullable=False, index=True)
    crypto_names: Mapped["CryptoPairName"] = relationship(back_populates="supported_exchanges")
