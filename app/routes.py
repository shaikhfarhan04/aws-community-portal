import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import select
from .extensions import db
from .models import UploadedFile
from .storage import upload, download_url, client
main_bp=Blueprint('main',__name__)
@main_bp.get('/')
def index(): return render_template('index.html')
@main_bp.get('/health')
def health(): return {'status':'ok'},200
def allowed(name): return bool(name and '.' in name and name.rsplit('.',1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])
@main_bp.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    if request.method=='POST':
        incoming=[f for f in request.files.getlist('documents') if f and f.filename]
        if not incoming: flash('Choose at least one file.','error'); return redirect(url_for('main.dashboard'))
        if len(incoming)>10: flash('Upload up to 10 files at a time.','error'); return redirect(url_for('main.dashboard'))
        prepared=[]
        for f in incoming:
            name=secure_filename(f.filename)
            if not allowed(name): flash(f'File type not allowed: {f.filename}','error'); return redirect(url_for('main.dashboard'))
            f.stream.seek(0,os.SEEK_END); size=f.stream.tell(); f.stream.seek(0)
            if size<=0 or size>10*1024*1024: flash(f'{name} must be 1 byte to 10 MB.','error'); return redirect(url_for('main.dashboard'))
            prepared.append((f,name,size))
        keys=[]
        try:
            for f,name,size in prepared:
                key,ctype=upload(f,current_user.id,name); keys.append(key)
                db.session.add(UploadedFile(member_id=current_user.id,original_filename=name,s3_key=key,content_type=ctype,file_size=size))
            db.session.commit(); flash(f'Uploaded {len(prepared)} file(s).','success')
        except Exception:
            db.session.rollback(); current_app.logger.exception('Upload failed')
            try:
                for key in keys: client().delete_object(Bucket=current_app.config['S3_BUCKET_NAME'],Key=key)
            except Exception: current_app.logger.exception('Cleanup failed; check for orphaned S3 objects')
            flash('Upload failed. Check S3 permissions, RDS access and application logs.','error')
        return redirect(url_for('main.dashboard'))
    files=db.session.scalars(select(UploadedFile).where(UploadedFile.member_id==current_user.id).order_by(UploadedFile.created_at.desc())).all()
    return render_template('dashboard.html',files=files)
@main_bp.post('/files/<int:file_id>/download')
@login_required
def file_download(file_id):
    record=db.session.get(UploadedFile,file_id)
    if record is None or record.member_id!=current_user.id: abort(404)
    try: return redirect(download_url(record.s3_key,record.original_filename))
    except Exception:
        current_app.logger.exception('Presigned URL generation failed'); flash('Download unavailable. Try again.','error'); return redirect(url_for('main.dashboard'))
