from .database import *
from .utils import files_req, files_opt

class File:
    def __init__(self, properties):
        self.properties = {}

        for property in files_req + files_opt:
            try:
                self.properties[property] = properties[property]
            except KeyError:
                self.properties[property] = None
            except Exception as e:
                print(f"Error fetching the property: {property}")
                self.properties[property] = None
    
    def update(self, **kwargs):
        try:
            cols = set(files_req + files_opt)
            for arg in kwargs:
                if arg not in cols:
                    return (False, f"Unknown property: {arg}")
                if arg in ('file_id', 'user_id, file_type', 'uploaded_at'):
                    return (False, f'{arg} is immutable.')
                
            db = Database()

            return db.update_file(self.properties['file_id'], kwargs)
        except Exception as e:
            return (False, f"Failed to update user: {e}")
    
    def delete(self):
        try:
            db = Database()
            return db.delete_file(self.properties['file_id'], self.properties['user_id'], self.properties['filename'])
        except Exception as e:
            return (False, f"Failed to delete user: {e}")