from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    # used for alembic migrations and ORM
    pass


class CryptoPairName(Base):
    __tablename__ = "crypto_pairs_names"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crypto_name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    # back populates
    supported_exchanges: Mapped[list["SupportedExchangesByCrypto"]] = relationship(
        back_populates="crypto_names", cascade="all, delete"
    )
    batch_stats: Mapped[list["BatchStatus"]] = relationship(back_populates="crypto_id_ref")


class SupportedExchangesByCrypto(Base):
    __tablename__ = "supported_exchanges_by_crypto"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crypto_id: Mapped[int] = mapped_column(ForeignKey("crypto_pairs_names.id"))
    supported_exchange: Mapped[str] = mapped_column(nullable=False, index=True)

    crypto_names: Mapped["CryptoPairName"] = relationship(back_populates="supported_exchanges")

    __table_args__ = (
        UniqueConstraint("crypto_id", "supported_exchange", name="unique_id_to_exchange"),
    )


class BatchStatus(Base):
    __tablename__ = "batch_status"

    id: Mapped[int] = mapped_column(
        ForeignKey(SupportedExchangesByCrypto.id),
        primary_key=True,
    )
    crypto_id: Mapped[int] = mapped_column(ForeignKey(CryptoPairName.id), nullable=False)
    interval: Mapped[str] = mapped_column(nullable=False)

    # actual status columns
    saved_cache: Mapped[bool] = mapped_column(nullable=False)
    difference_found: Mapped[bool] = mapped_column(nullable=False)
    saved_db: Mapped[bool] = mapped_column(nullable=False)

    crypto_id_ref: Mapped["CryptoPairName"] = relationship(back_populates="batch_stats")


class ComputedSpreadMax(Base):
    __tablename__ = "computed_spread_max"

    id: Mapped[int] = mapped_column(
        ForeignKey(CryptoPairName.id),
        primary_key=True,
    )
    time = mapped_column(TIMESTAMP, nullable=False)
    high_exchange_id: Mapped[int] = mapped_column(ForeignKey(SupportedExchangesByCrypto.id))
    low_exchange_id: Mapped[int] = mapped_column(ForeignKey(SupportedExchangesByCrypto.id))
    spread_percent: Mapped[float] = mapped_column(nullable=False)
