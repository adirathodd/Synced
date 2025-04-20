import os
from supabase import create_client, Client
from dotenv import load_dotenv
from .util import users_opt, users_req
import bcrypt
import logging
from typing import Tuple, Any, Dict
from postgrest.exceptions import APIError

load_dotenv()
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, )

    def hash(self, item: str):
        return bcrypt.hashpw(
            item.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def verify(self, username: str, password: str):
        """Verify a user's credentials."""
        try:
            response = (
                self.supabase
                    .table("users")
                    .select("password")
                    .eq("username", username)
                    .execute()
            )

            if not response.data:
                raise ValueError("incorrect username or password!")
            
            stored_hash = response.data[0]["password"]
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return
            
            raise ValueError("incorrect username or password!")
        except Exception as e:
            raise Exception(f"{str(e)}")

    def update_user(self, user_id: int, updates: dict):
        """Updates the given fields for a particular user."""
        try:
            allowed_fields = users_req + users_opt
            for key in updates:
                if key not in allowed_fields:
                    raise KeyError(f"Unexpected key in updates: {key}")

            if "password" in updates:
                updates["password"] = self.hash(updates["password"])

            response = (
                self.supabase
                    .table("users")
                    .update(updates)
                    .eq("id", user_id)
                    .execute()
            )

            if not response.data:
                raise KeyError(f"No user found with id: {user_id}")
        
            return (True, "User updated succesfully!")
        except Exception as e:
            return (False, f"Error updating user: {e}")

    def add_user(self, user_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Add a new user to the 'users' table."""

        new_user_req = {}
        for column in users_req:
            if column not in user_data:
                logger.error("Required field missing: %s", column)
                raise ValueError(f"Required field missing: {column}")
            new_user_req[column] = user_data[column]

        unexpected = [k for k in user_data if k not in users_req + users_opt]
        if unexpected:
            field = unexpected[0]
            logger.error("Unexpected field: %s", field)
            raise KeyError(f"Unexpected field: {field}")
        new_user_opt = {k: v for k, v in user_data.items() if k in users_opt}

        new_user = {**new_user_req, **new_user_opt}
        new_user["password"] = self.hash(new_user["password"])

        # Check if username already exists
        try:
            exists_resp = (
                self.supabase
                    .table("users")
                    .select("id")
                    .eq("username", new_user["username"])
                    .execute()
            )
            if exists_resp.data:
                logger.error("Username already exists: %s", new_user["username"])
                raise ValueError("username already exists")
        except APIError as err:
            logger.error("Error checking username existence: %s", err)
            raise Exception("Error verifying username: {err}")

        # Check if email already exists
        try:
            exists_resp = (
                self.supabase
                    .table("users")
                    .select("id")
                    .eq("email", new_user["email"])
                    .execute()
            )
            if exists_resp.data:
                logger.error("Email already exists: %s", new_user["email"])
                raise ValueError("email already exists")
        except APIError as err:
            logger.error("Error checking email existence: %s", err)
            raise Exception(f"Error verifying email: {err}")

        try:
            response = (
                self.supabase
                    .table("users")
                    .insert(new_user)
                    .execute()
            )
        except APIError as err:
            logger.error("Supabase insert error: %s", err)
            raise Exception(f"error creating the user: {err}")
        
        if not response.data:
            logger.error("No data returned on insert.")
            raise Exception("error creating the user: no data returned")

        return 

    def remove_user(self, field: str, value: str):
        """Remove a user from the 'users' table by a given field
            Field Key = column name
            Field Value = value
        """
        try:
            response = (
                self.supabase
                    .table("users")
                    .delete()
                    .eq(field, value)
                    .execute()
            )

            if not response.data:
                raise KeyError(f"no user found with {field}: {value}")
            
            return (True, "user deleted!")
        except Exception as e:
            return (False, f"error deleting the user: {e}")
    
    def verify_email(self, email: str):
        try:
            response = (
                self.supabase
                    .table("users")
                    .update({"verified": True})
                    .eq("email", email)
                    .execute()
            )

            if not response.data:
                raise KeyError(f"no user found with email: {email}")

            return (True, "email verified!")
        except Exception as e:
            return (False, f"error verifying the email: {e}")

if __name__ == '__main__':
    um = UserManager()
    
    # Example: List all users
    # response = um.list_users()
    # print("Current users:", response)
    
    # Example: Add a new user (uncomment to use)
    # new_user = {"username": "john_doe", "email": "john@example.com", "password": "hello", "first_name": "John",
    #             "last_name": "Doe"}
    # print("Added user:", um.add_user(new_user))
    
    # Example: Remove a user by id (uncomment to use)
    # print("Removed user:", um.remove_user(5))