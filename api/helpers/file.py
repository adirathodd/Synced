import database
from utils import files_req, files_opt

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
                if arg == 'storage_id':
                    return (False, 'Storage ID is immutable.')
                if arg not in cols:
                    return (False, f"Unknown property: {arg}")
                
            db = database.Database()

            return db.update_file(self.properties['storage_id'], kwargs)
        except Exception as e:
            return (False, f"Failed to update user: {e}")
    
    def delete(self):
        try:
            storage_id = self.properties['storage_id']
            db = database.Database()
            return db.delete_file(storage_id)
        except Exception as e:
            return (False, f"Failed to delete user: {e}")