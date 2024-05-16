from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List


# data models
class Base(DeclarativeBase):
    pass


class Friendship(Base):
    __tablename__ = "friendship"
    user1 = mapped_column(ForeignKey("user.username"), primary_key=True)
    user2 = mapped_column(ForeignKey("user.username"), primary_key=True)


class PendingFriendRequest(Base):
    __tablename__ = "pending_friend_request"
    user1 = mapped_column(ForeignKey("user.username"), primary_key=True)
    user2 = mapped_column(ForeignKey("user.username"), primary_key=True)


class User(Base):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str]
    account_type: Mapped[str] = mapped_column(default="student")
    mute_status: Mapped[bool] = mapped_column(default=False)
    friends: Mapped[List["User"]] = relationship(
        "User",
        secondary=Friendship.__tablename__,
        primaryjoin=username == Friendship.user1,
        secondaryjoin=username == Friendship.user2,
    )

    pending_friends: Mapped[List["User"]] = relationship(
        "User",
        secondary=PendingFriendRequest.__tablename__,
        primaryjoin=username == PendingFriendRequest.user1,
        secondaryjoin=username == PendingFriendRequest.user2,
    )
    room = mapped_column(ForeignKey("room.id"), nullable=True)


class Message(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender = mapped_column(ForeignKey("user.username"))
    message: Mapped[str]
    room_id = mapped_column(ForeignKey("room.id"))


class Room(Base):
    __tablename__ = "room"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    messages: Mapped[List["Message"]] = relationship("Message")
    user1 = mapped_column(ForeignKey("user.username"), nullable=True)
    user2 = mapped_column(ForeignKey("user.username"), nullable=True)


class Article(Base):
    __tablename__ = "article"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author = mapped_column(ForeignKey("user.username"))
    title: Mapped[str]
    content: Mapped[str]

    author_obj: Mapped[User] = relationship("User")
    comment_objs: Mapped[List["Comment"]] = relationship("Comment")


class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id = mapped_column(ForeignKey("article.id"))
    author = mapped_column(ForeignKey("user.username"))
    content: Mapped[str]

    article_obj: Mapped["Article"] = relationship(back_populates="comment_objs")
    author_obj: Mapped["User"] = relationship("User")