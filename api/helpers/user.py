from utils import users_req, users_opt
import database

class User:
    def __init__(self, properties: dict):
        self.properties = {}

        for property in users_req + users_opt:
            try:
                self.properties[property] = properties[property]
            except KeyError:
                self.properties[property] = None
            except Exception as e:
                print(f"Error fetching the property: {property}")
                self.properties[property] = None
    
    def update(self, **kwargs):
        try:
            cols = set(users_req + users_opt)
            for arg in kwargs:
                if arg == 'id':
                    return (False, 'User ID is immutable.')
                if arg not in cols:
                    return (False, f"Unknown property: {arg}")
                
            db = database.Database()

            return db.update_user(self.properties['id'], kwargs)
        except Exception as e:
            return (False, f"Failed to update user: {e}")
    
    def delete(self):
        try:
            id = self.properties['id']
            db = database.Database()
            return db.delete_user(id)
        except Exception as e:
            return (False, f"Failed to delete user: {e}")