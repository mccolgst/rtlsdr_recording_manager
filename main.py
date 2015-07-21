from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import Schedule, Recording
from croniter import croniter
from datetime import datetime

# set up the app object config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.debug = True
app.secret_key = 'secret town'


# create the db
db = SQLAlchemy(app)

# initialize the admin app
admin = Admin(app)
admin.add_view(ModelView(Schedule, db.session))
admin.add_view(ModelView(Recording, db.session))


@app.route("/")
def main():
    schedules = Schedule.query.all()
    now = datetime.now()
    for schedule in schedules:
        iterator = croniter(schedule.cron_schedule, now)
        schedule.next_launch = iterator.get_next(datetime)
        print schedule.next_launch
    return render_template("index.html", schedules=Schedule.query.all())


@app.route("/schedule/<int:schedule_id>")
def schedule_view(schedule_id):
    return render_template("schedule.html", schedule=Schedule.query.get(schedule_id))


if __name__ == "__main__":
    app.run('0.0.0.0')
