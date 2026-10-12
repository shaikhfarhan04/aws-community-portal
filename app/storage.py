import os, uuid, boto3
from flask import current_app
def client(): return boto3.client('s3', region_name=current_app.config['AWS_REGION'])
def upload(file_obj, member_id, filename):
    bucket=current_app.config['S3_BUCKET_NAME']
    if not bucket: raise RuntimeError('S3_BUCKET_NAME is not configured')
    ext=os.path.splitext(filename)[1].lower(); key=f'members/{member_id}/documents/{uuid.uuid4().hex}{ext}'
    content_type=file_obj.mimetype or 'application/octet-stream'
    client().upload_fileobj(file_obj.stream,bucket,key,ExtraArgs={'ContentType':content_type,'ServerSideEncryption':'AES256'})
    return key,content_type
def download_url(key, filename):
    return client().generate_presigned_url('get_object',Params={'Bucket':current_app.config['S3_BUCKET_NAME'],'Key':key,'ResponseContentDisposition':f'attachment; filename="{filename}"'},ExpiresIn=300)
