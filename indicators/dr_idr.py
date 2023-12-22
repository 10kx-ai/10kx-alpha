import pandas as pd

# Implementation was confirmed by jasongoodwin against jan1 2023 btc vs M4ster's TV implementation.

# Fixme the start time for extend is the same as time end

# "Regular" - nyse hours
#   regularTime         = input.session('0930-1030', 'RDR Time', group=GRP1)
#   regularExtend       = input.session('1030-1600', 'RDR Lines Time', group=GRP1)
rdr_time_start_hour = 14
rdr_time_start_minute = 30
rdr_time_end_hour = 15
rdr_time_end_minute = 30
rdr_extend_start_hour = 15
rdr_extend_start_minute = 30
rdr_extend_end_hour = 21
rdr_extend_end_minute = 30

# "After" - asia hours
#   afterTime           = input.session('1930-2030', 'ADR Time', group=GRP1)
#   afterExtend         = input.session('2030-0200', 'ADR Lines Time', group=GRP1)
adr_time_start_hour = 0
adr_time_start_minute = 30
adr_time_end_hour = 1
adr_time_end_minute = 30
adr_extend_start_hour = 1
adr_extend_start_minute = 30
adr_extend_end_hour = 7
adr_extend_end_minute = 0

# "Overnight" - europe hours
#   overnightTime       = input.session('0300-0400', 'ODR Time', group=GRP1)
#   overnightExtend     = input.session('0400-0830', 'ODR Lines Time', group=GRP1)
odr_time_start_hour = 8
odr_time_start_minute = 0
odr_time_end_hour = 9
odr_time_end_minute = 0
odr_extend_start_hour = 9
odr_extend_start_minute = 0
odr_extend_end_hour = 13
odr_extend_end_minute = 30

def minute_of_day(hour, minute):
    return hour * 60 + minute

def is_rdr_time_start(date):
    if minute_of_day(rdr_time_start_hour, rdr_time_start_minute) <= \
        minute_of_day(date.hour, date.minute) < \
            minute_of_day(rdr_time_end_hour, rdr_time_end_minute):
        return True

def is_rdr_time_extend(date):
    if minute_of_day(rdr_extend_start_hour, rdr_extend_start_minute) <= \
        minute_of_day(date.hour, date.minute) < \
            minute_of_day(rdr_extend_end_hour, rdr_extend_end_minute):
        return True

def is_adr_time_start(date):
    if minute_of_day(adr_time_start_hour, adr_time_start_minute) <= \
        minute_of_day(date.hour, date.minute) < \
            minute_of_day(adr_time_end_hour, adr_time_end_minute):
        return True

def is_adr_time_extend(date):
    if minute_of_day(adr_extend_start_hour, adr_extend_start_minute) <= \
        minute_of_day(date.hour, date.minute) < \
            minute_of_day(adr_extend_end_hour, adr_extend_end_minute):
        return True

def is_odr_time_start(date):
    if minute_of_day(odr_time_start_hour, odr_time_start_minute) <= \
        minute_of_day(date.hour, date.minute) < \
            minute_of_day(odr_time_end_hour, odr_time_end_minute):
        return True

def is_odr_time_extend(date):
    if minute_of_day(odr_extend_start_hour, odr_extend_start_minute) <= \
        minute_of_day(date.hour, date.minute) < \
            minute_of_day(odr_extend_end_hour, odr_extend_end_minute):
        return True

# To allow this to work on all timeframes, currently only DR is implemented, not IDR
# May have issues w/ 4h - have to check...
def dr_idr(df: pd.DataFrame=None):
    dr_high_price = 0
    dr_low_price = 0
    is_dr_high_crossed = 0
    is_dr_low_crossed = 0

    dr_high = []
    dr_low = []
    dr_high_crossed = []
    dr_low_crossed = []
    dr_high_diff = []
    dr_low_diff = []

    # TODO test it's 5m data - should only be used on 5m.
    # IDR will only work on 5m. DR will only work on <=30m.
    for index, row in df.iterrows():
        if is_rdr_time_start(index) or \
                is_adr_time_start(index) or \
                is_odr_time_start(index):

            if dr_high_price < row['high']:
                dr_high_price = row['high']

            if dr_low_price == 0 or dr_low_price > row['low']:
                dr_low_price = row['low']

            dr_high.append(0)
            dr_low.append(0)
            dr_high_diff.append(0)
            dr_low_diff.append(0)

        elif is_rdr_time_extend(index) or \
                is_adr_time_extend(index) or \
                is_odr_time_extend(index):

            if dr_high_price < row['close']:
                is_dr_high_crossed = 1

            elif dr_low_price > row['close']:
                is_dr_low_crossed = 1

            dr_high_diff.append(row['close'] - dr_high_price)
            dr_low_diff.append(row['close'] - dr_low_price)
            dr_high.append(dr_high_price)
            dr_low.append(dr_low_price)

        else:
            # ensure the crossed signal is reset between sessions
            is_dr_high_crossed = 0
            is_dr_low_crossed = 0
            dr_high_price = 0
            dr_low_price = 0
            dr_high.append(0)
            dr_low.append(0)
            dr_high_diff.append(0)
            dr_low_diff.append(0)

        dr_high_crossed.append(is_dr_high_crossed)
        dr_low_crossed.append(is_dr_low_crossed)

    return dr_high, dr_low, dr_high_crossed, dr_low_crossed, dr_high_diff, dr_low_diff