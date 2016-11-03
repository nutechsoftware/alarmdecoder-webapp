from datetime import datetime, timedelta

def check_time_restriction(start_time, end_time):
    st = start_time.split(':')
    et = end_time.split(':')

    message_time = datetime.now()
    start_time = message_time.replace(hour=int(st[0]), minute=int(st[1]), second=int(st[2]), microsecond=0)
    end_time = message_time.replace(hour=int(et[0]), minute=int(et[1]), second=int(et[2]), microsecond=0)

    # Tweak the date if the time range spans midnight
    if end_time.hour < start_time.hour:
        # If check time is after midnight, move start time back to the previous day
        if message_time.hour < end_time.hour:
            start_time -= timedelta(days=1)
        # .. and if before midnight, move end time to the next day.
        else:
            end_time += timedelta(days=1)

    if start_time <= message_time <= end_time:
        return True

    return False
