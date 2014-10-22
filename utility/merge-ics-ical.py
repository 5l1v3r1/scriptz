#!/usr/bin/python
#
#   merge_ics.py:   This script will get all .ics files (iCalendar files, as
#                   specified in the RFC 2445 specification), read it and
#                   aggregate all events to a new .ics file. If one of the
#                   sourcefiles is not readable (or is not RFC 2445 compatible),
#                   it will be ignored.
#                   Please note, that this script currently only supports the VEVENT-tag.
#                   Nothing else (this means: no todo's etc...).
#
#   Requires:       python-icalendar
#
#   Usage:          Configure options in merge-ics-ical.cfg. There are no command-line arguments.
#
#   Source:         https://merge-ics.googlecode.com/svn/trunk
#
#
#   Copyright:      (C) 2007 by Thomas Deutsch <thomas@tuxpeople.org>
#
#   Version:        1.7(2007-05-28)
#
#   License:        GPL v2 -- http://www.gnu.org/licenses/gpl-2.0.html
#
#                   This program is free software; you can redistribute it and/or modify
#                   it under the terms of the GNU General Public License as published by
#                   the Free Software Foundation; either version 2 of the License, or
#                   (at your option) any later version.
#
#                   This program is distributed in the hope that it will be useful, but
#                   WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#                   or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
#                   for more details.
#
#                   You should have received a copy of the GNU General Public License along
#                   with this program; if not, write to the Free Software Foundation, Inc.,
#                   51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
#   Credits:        My thank goes to (list not in a specific order):
#                    - Max M (iCalendar Package)
#                    - Christof Buergi (Codecontributions)
#                    - Michael Naef (Useful tipps)
#                    - Rolf Pfister (Useful tipps)
#                    - Andreas Ahlenstorf (Useful tipps, and he has told me how easy python is. That's why I'm using it...)
#                    - Dieter Wirz (testing on MacOS, tipps)
#                    - Beat Wirthlin (added features to ignore historic and duplicted events, script refactoring)
#                    - and all other helpers ;)


# Where is the configuration?
CONF = 'merge-ics-ical.cfg'

#############################
# Script:                   #
#############################

DEBUGMSG = 'Log started\n'

# Read the config
DEBUGMSG += 'try to read config\n'
try:
    execfile(CONF)
except:
    print MY_SHORTNAME + ': Error, unable to read config: ', sys.exc_info()[1]

# imports
import glob, sys, datetime

DEBUGMSG += 'start init\n'

now = datetime.datetime.now()
DEBUGMSG += now.strftime('now: %Y/%m/%d - %H:%M:%S') + '\n'
# limit
limitdate = now - datetime.timedelta(days=HISTORY_DAYS)
limit = limitdate.strftime('%Y%m%d')
if HISTORY_DAYS > 0:
    DEBUGMSG += '- ignore events before ' + limitdate.strftime('%Y/%m/%d') + '\n'
# this set will be used fo find duplicate events
eventSet = set()
if IGNORE_DUPLICATE:
    DEBUGMSG += '- ignore duplicated events\n'
DEBUGMSG += 'init done\n'

# We need the iCalendar package from http://codespeak.net/icalendar/
from icalendar import Calendar, Event, Timezone

# Open the new calendarfile and adding the information about this script to it
newcal = Calendar()
newcal.add('prodid', '-//' + MY_NAME + '//' + MY_DOMAIN + '//')
newcal.add('version', '2.0')
newcal.add('x-wr-calname', CALENDARNAME)
DEBUGMSG += 'new calendar ' + ICS_OUT + ' started\n'

# we need to add a timezone, because some clients want it (e.g. sunbird 0.5)
newtimezone = Timezone()
newtimezone.add('tzid', OUR_TIMEZONE)
newcal.add_component(newtimezone)

# Looping through the existing calendarfiles
for s in glob.glob(CALDIR + '*.ics'):
    try:
        # open the file and read it
        calfile = open(s,'rb')
        cal = Calendar.from_string(calfile.read())
        DEBUGMSG += 'reading file ' + s + '\n'
        # every part of the file...
        for component in cal.subcomponents:
            # ...which name is VEVENT will be added to the new file
            if component.name == 'VEVENT':
                try:
                    if HISTORY_DAYS > 0:
                        eventStart = component.decoded('dtstart').strftime('%Y%m%d')
                        if eventStart < limit:
                            eventId = str(component['dtstart']) + ' | ' + str(component['dtend']) + ' | ' + str(component['summary'])
                            DEBUGMSG += '  skipped historic event before ' + limit + ' : ' + eventId + '\n'
                            continue
                    if IGNORE_DUPLICATE:
                        eventId = str(component['dtstart']) + ' | ' + str(component['dtend']) + ' | ' + str(component['summary'])
                        if eventId not in eventSet:
                            eventSet.add(eventId)
                        else:
                            DEBUGMSG += '  skipped duplicated event: ' + eventId + '\n'
                            continue
                except:
                    # ignore events with missing dtstart, dtend or summary
                    DEBUGMSG += ' ! skipped an event with missing dtstart, dtend or summary. likely historic or duplicated event.\n'
                    continue
                newcal.add_component(component)
        # close the existing file
        calfile.close()
    except:
        # if the file was not readable, we need a errormessage ;)
        print MY_SHORTNAME + ': Error: reading file:', sys.exc_info()[1]
        print s


# After the loop, we have all of our data and can write the file now
try:
    f = open(ICS_OUT, 'wb')
    f.write(newcal.as_string())
    f.close()
    DEBUGMSG += 'new calendar written\n'
except:
    print MY_SHORTNAME + ': Error: ', sys.exc_info()[1]

if DEBUG == True:
    try:
        l = open(DEBUGFILE, 'wb')
        l.write(DEBUGMSG)
        l.close()
    except:
        print MY_SHORTNAME + ': Error, unable to write log: ', sys.exc_info()[1]
# all done...

#### CHANGEGLOG ###############################################################
#
# merge_ics 1.7 (in development)
# ==============================
#
# * fix for issue 3 "NameError: name 'Timezone' is not defined" (thanks to jjspreij)
# * feature to ignore historic events
# * feature to ignore duplicated events
# * script clean up
#
# merge_ics 1.6 (2007-07-09)
# ==========================
#
# * Wrote warning into README regarding the VEVENT 'thing'
# * split up header into different fiels (dependencies, credits etc...)
# * fixed bug with timezone (sunbird wants a VTIMEZONE section, now we have one)
# * Added Time/Date to debug output