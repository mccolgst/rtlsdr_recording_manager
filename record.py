import subprocess
import argparse
import time
from models import db, Recording
import os, uuid

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='record some radio')
    parser.add_argument('frequency', metavar='f', type=str, help='frequency to record in MHz ex 96.3e6')
    parser.add_argument('seconds', metavar='t', type=int, help='number of seconds to record ex 5')
    parser.add_argument('--schedule_id', type=int, help='optional id of schedule that kicked off this recording')
    parser.add_argument('--outfile', type=int, help='optional file location to record to')

    args = parser.parse_args()

    # assign an outfile name if not specified
    if args.outfile:
        outfile = args.outfile
    else:
        outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'recordings',
                               str(uuid.uuid4()))
        # TODO: add more descriptive outfile name to associate with schedule

    if args.schedule_id:
        # create a recording object in the db
        recording = Recording(schedule_id=args.schedule_id, recorded_file=outfile)
        db.session.add(recording)
        db.session.commit()

    command = '/usr/local/bin/rtl_fm -f {} -M wbfm -s 200000 -r 48000 - '.format(str(args.frequency))
    with open(outfile, 'wb') as of:
        p = subprocess.Popen('exec ' + command, shell=True, stdout=of)
    time.sleep(args.seconds)
    p.kill()
