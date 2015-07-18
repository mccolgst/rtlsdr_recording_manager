from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sqlalchemy import event
from crontab import CronTab
import os, sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
cron = CronTab(user=True)
command_template = '{} {}/record.py {} {} --schedule_id {}'
# use schedule_<id> comment for easy lookup later on for CRUD ops
comment_template = 'schedule_{}'


def _render_cron_command(schedule_object):
    return command_template.format(sys.executable,
                                   os.path.dirname(os.path.realpath(__file__)),
                                   schedule_object.frequency,
                                   schedule_object.duration_seconds,
                                   schedule_object.id,
                                   schedule_object.id)


def _find_cron_by_schedule_id(schedule_id):
    print schedule_id
    print comment_template.format(schedule_id)
    iterator = cron.find_comment(comment_template.format(schedule_id))
    job = [job for job in iterator][0]  # cron find returns an iterator so THIS is awkward.
    return job


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    frequency = db.Column(db.String)
    duration_seconds = db.Column(db.Integer)
    cron_schedule = db.Column(db.String)
    enabled = db.Column(db.Boolean)

    # delete recordings when it's parent schedule is deleted
    recordings = db.relationship('Recording',
                                 backref='user',
                                 cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "<Schedule {} at {} \
               for {} seconds - cron: {}>".format(self.name,
                                                  self.frequency,
                                                  self.duration_seconds,
                                                  self.cron_schedule)


@event.listens_for(Schedule, 'after_insert')
def new_cron(mapper, connection, target):
    command = _render_cron_command(target)
    job = cron.new(command=command)
    job.set_comment(comment_template.format(target.id))
    job.setall(target.cron_schedule)
    job.enable(target.enabled)
    cron.write()


@event.listens_for(Schedule, 'after_update')
def update_cron(mapper, connection, target):
    new_command = _render_cron_command(target)
    job = _find_cron_by_schedule_id(target.id)
    # set command, command and schedule
    job.set_command(new_command)
    job.set_comment(comment_template.format(target.id))
    job.setall(target.cron_schedule)
    job.enable(target.enabled)
    cron.write()


@event.listens_for(Schedule, 'after_delete')
def delete_cron(mapper, connection, target):
    job = _find_cron_by_schedule_id(target.id)
    # remove the cron we found
    cron.remove(job)
    cron.write()


class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recorded_file = db.Column(db.String)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    # delete recordings when a schedule is deleted


@event.listens_for(Recording, 'after_delete')
def delete_recorded_file(mapper, connection, target):
    # delete associated recording file
    try:
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'recordings',
                               target.recorded_file))
    except OSError:
        # I don't really care about this yet
        pass
