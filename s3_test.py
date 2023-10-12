import boto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID =os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
client = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_DEFAULT_REGION
                      )

file_name = 'test.jpeg'      # 업로드할 파일 이름 
bucket = 'jungle-til'           #버켓 주소
key = 'test.jpeg' # s3 파일 이미지

image_url = f'https://{bucket}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{key}'
print(image_url)
print(AWS_ACCESS_KEY_ID)
# client.upload_file(file_name, bucket, key) #파일 저장