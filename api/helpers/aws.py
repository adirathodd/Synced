import boto3
import botocore
import botocore.exceptions
from dotenv import load_dotenv
import os
from .utils import is_image, is_video

load_dotenv()

class AWS:
    def __init__(self):
        self.bucket_name = os.getenv('BUCKET_NAME')
        self.aws_obj = boto3.client('s3')
        
    def key_exists(self, s3_key):
        try:
            self.aws_obj.head_object(Bucket=self.bucket_name, Key=s3_key)

            # Key already exists
            return (1, 'Check successful')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Key does not exsit
                return (0, 'Check successful')
            else:
                # Something went wrong
                return (-1, f'{e}')

    def upload_file(self, username, filepath):
        try:
            if not os.path.exists(filepath):
                return (False, "Filepath does not exist!")
            
            # Parameters for uploading file
            s3_key = f'test/{username}/'

            filename = os.path.basename(filepath)
            
            # Validate if file is image or video
            if is_image(filepath):
                s3_key += 'images/'
            elif is_video(filepath):
                s3_key += 'videos/'
            
            # Check failed
            else:
                return (False, 'Not a valid filetype!')
            
            s3_key += f'{filename}'
            code, message = self.key_exists(s3_key)

            if code == 1:
                return (False, 'File with the same name already exists!')
            elif code == -1:
                return (False, f'Something went wrong: {message}')

            self.aws_obj.upload_file(filepath, self.bucket_name, s3_key)

            return (True, "Upload Successful!")
        except Exception as e:
            return (False, f'Error uploading the file: {e}')

    def delete_file(self, username, filename):
        try:
            s3_key = f'test/{username}/'

            # Validate if file is image or video
            if is_image(filename):
                s3_key += 'images/'
            elif is_video(filename):
                s3_key += 'videos/'
            
            # Check failed
            else:
                return (False, 'Not a valid filetype!')
            
            s3_key += f'{os.path.basename(filename)}'

            code, message = self.key_exists(s3_key)

            if code == 0:
                return (False, 'File does not exist!')
            elif code == -1:
                return (False, f'Something went wrong: {message}')

            self.aws_obj.delete_object(Bucket=self.bucket_name, Key=s3_key)

            return (True, "Deletion Successful!")
        except Exception as e:
            return (False, f"Error deleting the file: {e}")

if __name__ == '__main__':
    # Test cases
    add1 = '/Users/adirathodd/Desktop/synced.JPG'
    add2 = '/Users/adirathodd/Desktop/schedule.JPG'

    delete1 = 'synced.JPG'
    delete2 = 'schedule.JPG'

    user = 'adirathodd'

    engine = AWS()

    print(add1, engine.upload_file(user, add1))
    print(add2, engine.upload_file(user, add2))
    print(delete1, engine.delete_file(user, delete1))
    print(delete2, engine.delete_file(user, delete2))