import exifread
import os
import re
from datetime import datetime
import time
import pytz

_utc = pytz.timezone('UTC')


def exif_datetime_to_timestamp(exif_datetime, tzinfo):
    dt = datetime.strptime(exif_datetime, '%Y:%m:%d %H:%M:%S')

    if hasattr(tzinfo, 'localize'):
        dt = tzinfo.localize(dt)
    else:
        dt = dt.replace(tzinfo=tzinfo)

    return dt


def get_exif_datetime(path, tzinfo):
    dttags = ['Image DateTime', 'EXIF DateTimeOriginal',
            'EXIF DateTimeDigitized']
    with open(path, mode='rb') as f:
        tags = exifread.process_file(f)
        for dttag in dttags:
            if dttag in tags:
                return exif_datetime_to_timestamp(str(tags[dttag]), tzinfo)

    return None


def probe_picture_datetime(path, tzinfo, fast=False, touch=False):

    if fast:
        touch = False

    dt = None

    if not fast:
        dt = get_exif_datetime(path, tzinfo)

    if not dt:
        dt = datetime.utcfromtimestamp(os.path.getmtime(path)).replace(tzinfo=pytz.utc).astimezone(tzinfo)

    if touch:
        mtime=dt.timestamp()
        os.utime(path, times=(int(time.time()), mtime))

    return dt


def group(source, sep):
    last = None
    result = []
    try:
        while True:
            item = next(source)
            if last != None and sep(item, last):
                yield result
                result = []
            result.append(item)
            last = item
    except StopIteration:
        yield result


def categorize(source, target, sep=24*60*60, timezone=None, fast=False, touch=False, renumber=False):
    if isinstance(timezone, str):
        timezone = pytz.timezone(timezone)

    fnptn = re.compile('(?!\\.).*\\.(?i)(jpeg|jpg)')

    pathgen = \
            (path
                    for path in 
                        (os.path.join(dirpath, filename)
                            for dirpath, dirname, filenames in os.walk(source)
                            for filename in filenames
                            if fnptn.match(filename))
                    if os.path.isfile(path))

    pics = []

    for path in pathgen:
        dt = probe_picture_datetime(path, timezone, fast, touch)

        if not dt:
            continue

        pics.append((dt, path))

    pics.sort()

    for grp in group(iter(pics), lambda n, o: o[0].timestamp() + sep <= n[0].timestamp()):
        day_from = grp[0][0].strftime('%Y%m%d')
        day_to = grp[-1][0].strftime('%Y%m%d')

        if day_from == day_to:
            to = day_from
        else:
            to = day_from + '-' + day_to

        to = os.path.join(target, to)
        if not os.path.exists(to):
            os.mkdir(to)

        i = 1
        zfl = len(str(len(grp)))
        for dt, path in grp:
            if renumber:
                fn = str(i).zfill(zfl) + '.jpg'
            else:
                fn = os.path.basename(path)
            npath = os.path.join(to, fn)
            if not os.path.exists(npath):
                os.rename(path, npath)
            i += 1

# vim: ts=4 sw=4 et
