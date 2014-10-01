"""
Created on Oct 28, 2013

@author: Nathan S.
"""
import re
from datetime import date, timedelta
import sys


def extract(src):
    """
    @param src: html source to a MFP report
    @type src:
    @return:
    @rtype:
    """

    # Sloppy regexes
    # Todo- use XML parsing library instead of regex
    # 9/30/14 - XML parsing? pretty sure this is html
    date_re = re.compile(r'(?<=id="date">)(.*)</h2>')
    cal_re = re.compile(r'(?<=TOTAL:</td>)\s+<td>(\d*)(?:,*)(\d*)</td>')

    with open(src, 'r') as f:
        text = f.read()

    dates = date_re.findall(text)
    txt_cals = cal_re.findall(text)

    _int = int
    _join = ''.join

    cals = [_int(_join(x)) for x in txt_cals]

    assert len(dates) == len(cals)

    return dates, cals


class CalResult():
    def __init__(self, start_wt, end_wt, tdee, bulk_surplus=300):
        self.bulk_surplus = bulk_surplus
        self.start_wt = start_wt
        self.end_wt = end_wt
        self.tdee = tdee
        self.daily_bulk_surplus = tdee + bulk_surplus
        self.weekly_bulk_surplus = self.daily_bulk_surplus * 7 - 2500 * 7

    def __str__(self):
        return "Cal Result: '\n'%s\n" % '\n'.join("%s = %r" % (k, v) for k, v in vars(self).items())


def main():
    # mydate = date.today()
    # td = timedelta(days=1)
    # dateformat = "%B %d, %Y"

    mfp_doc = "C:\\Users\\Administrator\\Documents\\Programming\\docs\\output\\mfp_test.txt"

    dates, cals = extract(mfp_doc)
    total_cal = sum(cals)
    days = len(cals)
    ave_daily = total_cal / days
    lbs2cal = 3500  # lbs * <- == cals

    results = []; rap = results.append

    for start_wt in range(174, 177):
        for end_wt in range(179, 182):
            wt_diff = end_wt - start_wt
            surplus = wt_diff * lbs2cal
            daily_surplus = surplus / days
            tdee = ave_daily - daily_surplus

            print("Start:", start_wt, "End:", end_wt, "TDEE:", tdee)

            cal2bulk = (tdee + 300) * 7 - (2500 * 7)

            print("  ", "Weekly Bulk @ +300: +", cal2bulk, '\n', sep='')

            rap(CalResult(start_wt, end_wt, tdee, 300))

    return results

if __name__ == '__main__':
    main()




