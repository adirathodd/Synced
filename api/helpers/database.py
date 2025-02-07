import psycopg2
from dotenv import load_dotenv
import os
from utils import users_uniq, users_req, users_opt, files_opt, files_req, files_uniq, files_cols, users_cols
from user import User
from file import File
from AWS import AWS

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

dsn = (
    f'postgresql://postgres.vdzlvcxrjpjcaebjxaiv:{PASSWORD}@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
    #f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    f"?sslmode=require&gssencmode=disable"
)

aws_bucket = AWS()

class Database:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(dsn)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor() 
        except Exception as e:
            print("Connection failed:", e)
    
    ##############################################################
    ## ALL USER RELATED FUNCTIONS - create, delete, update, get ##
    ##############################################################

    def create_user(self, properties: dict):
        try:
            for column in users_req:
                if column not in properties:
                    return (False, f"Missing required property: {column}")
            
            properties_copy = properties.copy()

            # Check for unknown columns
            for column in properties_copy:
                if column not in users_cols:
                    return (False, f"Unknown column: {column}")


            columns = list(properties_copy.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            
            query = f"INSERT INTO users ({column_names}) VALUES ({placeholders});"
            values = [properties_copy[col] for col in columns]

            result = self.cursor.execute(str(query), values)
            
            if not result:
                return self.get_user(storage_id = properties['storage_id'])
            
            return (False, f"Something went wrong: {result}")

        except Exception as e:
            return (False, f'Failed to create user: {e}')

    def update_user(self, id: str, properties: dict):
        try:
            query = 'UPDATE users SET '

            for key, value in properties.items():
                query += f"{key} = '{value}', "

            query = query[:-2]
            query += f" WHERE id = {id};"

            res = self.cursor.execute(query)

            if not res:
                return (True, "User updated successfully!")

            return (False, "Something went wrong.")
        except Exception as e:
            return (False, f"Error updating the user fields: {e}")

    def get_user(self, **kwargs):
        try:
            res = None

            for key, value in kwargs.items():
                if key not in users_opt + users_req:
                    return (False, f"Unknown property: {key}", None)
                if key not in users_uniq:
                    return (False, f"The following property is not unique: {key}", None)
                
                if type(value) == int:
                    query = f"SELECT * FROM users WHERE {key} = {value};"
                else:
                    query = f"SELECT * FROM users WHERE {key} = '{value}';"

                res = self.cursor.execute(query)
                res = self.cursor.fetchall()

                if res:
                    break
            
            if not res:
                return (False, 'No matching user found!', None)
            
            properties = {}
            
            for idx, name in enumerate(users_req + users_opt):
                properties[name] = res[0][idx]

            user = User(properties)
            return (True, "User found", user)
        except Exception as e:
            return (False, f"Failed to get user: {e}", None)

    def delete_user(self, id: int):
        try:
            query = f'DELETE from users WHERE id = {id};'
        except Exception as e:
            return (False, f"Failed to delete user: {e}")

    ###############################################################
    ## ALL FILES RELATED FUNCTIONS - create, delete, update, get ##
    ###############################################################

    def get_files(self, **kwargs):
        try:
            res = None

            for key, value in kwargs.items():
                if key == 'username':
                    query = ''' 
                        SELECT * 
                        FROM files 
                        INNER JOIN users ON files.user_id = users.id
                        WHERE users.username = %s;
                    '''

                    res = self.cursor.execute(query, (value,))

                else:
                    if key !=key not in files_cols:
                        return (False, f"Unknown property: {key}", None)
                    
                    if type(value) == int:
                        query = "SELECT * FROM files WHERE %s = %s;"
                    else:
                        query = "SELECT * FROM files WHERE %s = '%s';"

                    res = self.cursor.execute(query, (key, value,))

                res = self.cursor.fetchall()

                if res:
                    break
            
            if not res:
                return (False, 'No matching file found!', None)
            
            files = []

            for i in range(len(res)):
                properties = {}
                
                for idx, name in enumerate(files_req + files_opt):
                    properties[name] = res[i][idx]

                files.append(File(properties))
    
            return (True, "File(s) found", files)
        except Exception as e:
            return (False, f"Failed to get files: {e}", None)

    def create_file(self, properties: dict):
        try:
            # Check for required columns
            for column in files_req:
                if column not in properties:
                    return (False, f"Missing required property: {column}")
            
            properties_copy = properties.copy()

            # Check for unknown columns
            for column in properties_copy:
                if column not in files_cols:
                    return (False, f"Unknown column: {column}")
            
            query = ''' 
                        SELECT username
                        FROM users 
                        WHERE id = %s;
                    '''

            res = self.cursor.execute(query, (properties['user_id'],))
            res = self.cursor.fetchall()

            result, message = aws_bucket.upload_file(res[0][0], properties['filename'])

            if not result:
                return (result, message, None)

            columns = list(properties_copy.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            
            query = f"INSERT INTO files ({column_names}) VALUES ({placeholders});"
            values = [properties_copy[col] for col in columns]

            result = self.cursor.execute(str(query), values)
            
            if not result:
                return (True, "File uploaded succesffully!")
            
            return (False, f"Something went wrong: {result}")
        except Exception as e:
            return (False, f"Unable to upload file: {e}")