#!/usr/bin/env python3
"""
Authentication module
"""
import uuid
import bcrypt

from db import DB
from user import User
from typing import TypeVar
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> bytes:
    """Hash a password with bcrypt for user
    Args:
       password (str): The password to hash
    Returns:
       bytes: The salted hash of the password
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def _generate_uuid() -> str:
    """generate uuid
    Returns:str: representation of a new UUID
    """
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """
    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> 'User':
        """Register a new user
        Args:
            email (str): The email address of the user
            password (str): The password of the user
        Returns:
            User: The newly created user
        Raises:
            ValueError: If a user with the same email already exists
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            pass
        return self._db.add_user(email, _hash_password(password))

    def valid_login(self, email: str, password: str) -> bool:
        """valid login of user
        Args:
            email (str): email of user
            password (str): password of user
        Returns:
            bool: [description]
        """
        try:
            user = self._db.find_user_by(email=email)
            if user:
                stored_password = user.hashed_password
                provided_password = password.encode('utf-8')
                if bcrypt.checkpw(provided_password, stored_password):
                    return True

        except NoResultFound:
            return False
        return False

    def create_session(self, email: str) -> str:
        """create a new session for user
        Args:
            email (str): email of user
        Returns:
            str: string representation of session ID
        """
        try:
            user = self._db.find_user_by(email=email)
            if user is None:
                return None
            else:
                session_id = _generate_uuid()
                self._db.update_user(user.id, session_id=session_id)
                return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> str:
        """get user from session id
        Args:
            session_id (str): session id of user
        Returns:
            str: user
        """
        if session_id is None:
            return
        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return
        return user

    def destroy_session(self, user_id: int) -> None:
        """destroy session
        Args:
            user_id (int): user id
        """
        try:
            user = self._db.find_user_by(id=user_id)
            self._db.update_user(user.id, session_id=None)
        except NoResultFound:
            pass

    def get_reset_password_token(self, email: str) -> str:
        """get reset password token
        Args:
            email (str): user email
        Raises:
            ValueError: if not found user
        Returns:
            str: reset token
        """
        try:
            user = self._db.find_user_by(email=email)
            reset_token = _generate_uuid()
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """update password

        Args:
            reset_token (str): reset token
            password (str): user password

        Raises:
            ValueError: if not found user
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            self._db.update_user(
                    user.id,
                    hashed_password=_hash_password(password),
                    reset_token=None
                    )
        except NoResultFound:
            raise ValueError
