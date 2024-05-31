#!/usr/bin/python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from user import Base, User
from typing import TypeVar


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database

        Args:
            email (str): The email address of the user
            hashed_password (str): The hashed password of the user

        Returns:
            current_user: The newly created User object
        """
        current_user = User(email=email, hashed_password=hashed_password)
        self._session.add(current_user)
        self._session.commit()
        return current_user

    def find_user_by(self, **kwargs) -> User:
        """Find a user by the given keyword arguments
        Args:
            **kwargs: The keyword arguments to filter the users by
        Returns:
            User: The first user found that matches the keyword arguments
        Raises:
            NoResultFound: If no user is found matching the keyword arguments
            InvalidRequestError: If the keyword arguments are invalid
        """
        try:
            find_user = self._session.query(User).filter_by(**kwargs).one()
        except NoResultFound:
            raise NoResultFound()
        except InvalidRequestError:
            raise InvalidRequestError()
        return find_user

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update a user's attributes
        Args: user_id (int): The ID of the user to update
              **kwargs: The keyword arguments to update the
              user's attributes with
        Raises:
            NoResultFound: If no user is found with the given user ID
            ValueError: If an invalid keyword argument is passed
        """
        user = self.find_user_by(id=user_id)
        for key, value in kwargs.items():
            if hasattr(User, key):
                setattr(user, key, value)
            else:
                raise ValueError(f"Invalid keyword argument '{key}'")
        self._session.commit()
        return None
