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

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frequency = db.Column(db.String)
    duration_seconds = db.Column(db.Integer)
    cron_schedule = db.Column(db.String)
    # name
    # active

    def __repr__(self):
        return "<Schedule at {} \
               for {} seconds - cron: {}>".format(self.frequency,
                                                    self.duration_seconds,
                                                    self.cron_schedule)

@event.listens_for(Schedule, 'after_insert')
def set_up_cron(mapper, connection, target):
    command = command_template.format(sys.executable,
                                      os.path.dirname(os.path.realpath(__file__)),
                                      target.frequency,
                                      target.duration_seconds,
                                      target.id)
    job = cron.new(command=command)
    job.setall(target.cron_schedule)
    print "about to write cron once"
    cron.write()

# TODO: update cron
#       delete cron
#       activate/deactivate cron

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recorded_file = db.Column(db.String)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
    schedule = db.relationship('Schedule', backref=db.backref('recordings', lazy='dynamic'))

# TODO: delete recordings hook to delete recording file

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)
