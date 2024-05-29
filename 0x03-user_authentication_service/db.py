#!/usr/bin/python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from user import Base


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

    def find_user_by(self, **kwargs) -> User:
        """Find a user by the given keyword arguments

        Args:
            **kwargs: The keyword arguments to filter the users by

        Returns:
            User: The first user found that matches the given keyword arguments

        Raises:
            NoResultFound: If no user is found that matches the given keyword arguments
            InvalidRequestError: If the keyword arguments are invalid
        """
        query = self._session.query(User)
        for key, value in kwargs.items():
            if hasattr(User, key):
                query = query.filter(getattr(User, key) == value)
            else:
                raise InvalidRequestError(f"Invalid keyword argument '{key}'")
        try:
            return query.one()
        except ORMNoResultFound:
            raise NoResultFound(f"No user found with the given keyword arguments: {kwargs}")

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database

        Args:
            email (str): The email address of the user
            hashed_password (str): The hashed password of the user

        Returns:
            User: The newly created User object
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user
