from models import db
import os

'''
    simple interim utility to recreate
    my database on the fly as I update
    the schema
'''


if __name__ == '__main__':
    try:
        os.remove('/tmp/test.db')
    except OSError:
        print 'db didn\'t exist!'

    db.create_all()
    print 'done!'
