import json
import sys
import time
from flask import render_template
from rq import get_current_job
from app import create_app, db, oa
from app.models import User, Post, Task, Hansard
from app.email import send_email
from app.rebuild import rebuild

app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(user_id):
    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Post.timestamp.asc()):
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)


        send_email('[Microblog] Your blog posts',
                sender=app.config['ADMINS'][0], recipients=[user.email],
                text_body=render_template('email/export_posts.txt', user=user),
                html_body=render_template('email/export_posts.html',
                                          user=user),
                attachments=[('posts.json', 'application/json',
                              json.dumps({'posts': data}, indent=4))],
                sync=True)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

def rebuild_hansard(user_id, *args, **kwargs ):
    print("I have started")
    try:
        _set_task_progress(0)
        dates = oa.get_debates("representatives",year=2020)
        dates = dates['dates']
        index = 0
        for date in dates:
            if Hansard.query.filter_by(date=date).first():
                print(date)
            else:
                rebuild(date)
            index += 1
            print("next hansard")
            _set_task_progress(100 * index // len(dates))
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
