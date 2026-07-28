from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

outfit_items = Table(
    "outfit_items",
    Base.metadata,
    Column("outfit_id", Integer, ForeignKey("outfits.id"), primary_key=True),
    Column("clothing_item_id", Integer, ForeignKey("clothing_items.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)

    clothing_items: Mapped[list["ClothingItem"]] = relationship(
        "ClothingItem", back_populates="user", cascade="all, delete-orphan"
    )
    outfits: Mapped[list["Outfit"]] = relationship(
        "Outfit", back_populates="user", cascade="all, delete-orphan"
    )


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    image_path: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="clothing_items")


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="outfits")
    items: Mapped[list["ClothingItem"]] = relationship("ClothingItem", secondary=outfit_items)
