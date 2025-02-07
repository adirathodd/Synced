from database import Database

# engine = Database()

# res = engine.execute('SELECT * FROM user_profile;')
# df = pd.DataFrame(res, columns=['id', 'username', 'email', 'password'])

# print(res)

# '''
# print(engine.get_user(id = 1))
# print(engine.get_user(username = 'adirathodd'))
# print(engine.get_user(email = 'adirathodd@gmail.com'))
# '''

if __name__ == '__main__':
    # user Test case
    # properties = {  'id': 0,
    #                 "username": 'adirathod99',
    #                 'email': 'adirathod99@gmail.com',
    #                 'password': 'Aditya1108!',
    #                 'first_name': 'Adi',
    #                 'middle_name': "A",
    #                 'last_name': 'Rathod'
    #             }

    db = Database()
    # # print(db.create_user(properties))
    # res, message, files = db.get_user(username = 'adirathod99')
    # # res, message = object.update(first_name = "Adi", email = "adirathod99@gmail.com")

   # files test case

    properties = {
            'storage_id': 1,
            'user_id': 1,
            'filename': '/Users/adirathodd/Desktop/synced.JPG',
            'filetype': 'JPG'
    }

    print(db.create_file(properties))