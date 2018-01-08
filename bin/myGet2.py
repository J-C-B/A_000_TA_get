__author__ = 'Michael Uschmann / MuS' 
__date__ = 'Copyright $Aug 25, 2017 7:48:46 PM$'
__version__ = '0.1'

import sys
import os
import json
import urllib2
import splunk.Intersplunk
import logging
import logging.handlers
import splunk.Intersplunk
import xml.dom.minidom
import xml.sax.saxutils
import collections
from datetime import datetime
from ConfigParser import SafeConfigParser
from optparse import OptionParser

# enable / disable logger debug output
myDebug='no' # debug disabled
#myDebug='yes' # debug enabled

# get SPLUNK_HOME form OS
SPLUNK_HOME = os.environ['SPLUNK_HOME']

# get myScript name and path
myScript = os.path.basename(__file__)
myPath = os.path.dirname(os.path.realpath(__file__))

# define the logger to write into log file
def setup_logging(n):
    logger = logging.getLogger(n)
    if myDebug == 'yes':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = '%s.log' % myScript
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = '%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s'
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger

# start the logger for troubleshooting
logger = setup_logging( 'Logger started ...' ) # logger

# starting the script
logger.info( 'Starting the get script ...' ) # logger

# get previous search results from Splunk
try: # lets do it
    logger.info( "getting previous search results..." ) # logger
    myresults,dummyresults,settings = splunk.Intersplunk.getOrganizedResults() # getting search results form Splunk
    for r in myresults: # loop the results
        logger.info( "Result is : %s" % r ) # logger
        for k, v in r.items(): # get key value pairs for each result
            logger.info( "Key is : %s | Value is : %s " % (k,v) ) # logger
            if k == "dest_lat": # get key
                r_dest_lat = v # set value
            if k == "dest_lon": # get key
                r_dest_lon = v # set value
            if k == "src_lat": # get key
                r_lat = v # set value
            if k == "src_lon": # get key
                r_lon = v # set value
            if k == "lat": # get key
                r_lat = v # set value
            if k == "lon": # get key
                r_lon = v # set value

except: # get error back
    logger.info( "INFO: no previous search results provided using [default]!" ) # logger

# or get user provided options in Splunk as keyword, option
try: # lets do it
    logger.info( 'getting Splunk options...' ) # logger
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions() # get key value pairs from user search
    logger.info( 'got these options: %s ...' % (options)) # logger
    section_name = options.get('me','moon') # get user option or use a default value
    logger.info( 'got these options: section_name = %s ...' % (section_name)) # logger
    forecast = options.get('forecast','no') # get user option or use a default value
    logger.info( 'got these options: forecast = %s ...' % (forecast)) # logger
    lat = options.get('lat','r_lat') # get user option or use a default value
    logger.info( 'got these options: lat = %s ...' % (lat)) # logger
    lon = options.get('lon','r_lon') # get user option or use a default value
    logger.info( 'got these options: lon = %s ...' % (lon)) # logger
    dest_lat = options.get('dest_lat','r_dest_lat') # get user option or use a default value
    dest_lon = options.get('dest_lon','r_dest_lon') # get user option or use a default value
    logger.info( 'got these options: %s %s %s %s %s ...' % (section_name, lat, lon, dest_lat, dest_lon)) # logger

except: # get error back
    logger.info( 'INFO: no option provided, using conf file!' ) # logger

# set path to inputs.conf file
try: # lets do it
    logger.info( 'read the inputs.conf...' ) # logger
    if os.path.isfile(os.path.join(myPath,'..','local','inputs.conf')): # do we have a local inputs.conf?
        configLocalFileName = os.path.join(myPath,'..','local','inputs.conf') # use it
    else: 
        configLocalFileName = os.path.join(myPath,'..','default','inputs.conf') # use the default one
    logger.info( 'inputs.conf file: %s' % configLocalFileName ) # logger
    parser = SafeConfigParser() # setup parser to read the inputs.conf
    parser.read(configLocalFileName) # read inputs.conf options
    if not os.path.exists(configLocalFileName): # if empty use settings from [default] stanza in inputs.conf
        splunk.Intersplunk.generateErrorResults(': No config found! Check your inputs.conf in local.') # print the error into Splunk UI
        exit(0) # exit on error

except Exception,e: # get error back
    logger.error( 'ERROR: No config found! Check your inputs.conf in local.' ) # logger
    logger.error( 'ERROR: %e' % e ) # logger
    splunk.Intersplunk.generateErrorResults(': No config found! Check your inputs.conf in local.') # print the error into Splunk UI
    sys.exit() # exit on error

# use user provided options or get stanza options
try: # lets do it
    logger.info( 'read the default options from inputs.conf...' ) # logger
    logger.info( 'reading server from inputs.conf...' ) # logger
    section_name = 'myGet://%s' % section_name
    server = parser.get(section_name, 'server')
    token = parser.get(section_name, 'token')
    #myDebug = parser.get(section_name, 'debug')
    logger.info( 'got these options: %s %s ...' % (server, token)) # logger

except Exception,e: # get error back
    logger.error( 'ERROR: unable to get default options from inputs.conf' ) # logger
    logger.error( 'ERROR: %e' % e ) # logger
    splunk.Intersplunk.generateErrorResults(': unable to get default options from inputs.conf') # print the error into Splunk UI
    sys.exit() # exit on error

# starting the main
logger.info( 'Starting the main task ...' ) 

# now we get data
try: # lets do it
    logger.info( 'getting data ...' ) 
    logger.info( 'using server %s ...' % server ) 
    logger.info( 'using token %s ...' % token ) 

    # getting moon phases
    if 'moon' in section_name:
        now = datetime.now()
        year = now.year
        con_str = '%s%s&token=%s' % (server,year, token)
        logger.info( 'using con_str %s ...' % con_str ) 
        url = urllib2.urlopen('%s' % con_str)
        r_parsed = json.loads(url.read())
        result = r_parsed['phasedata']
        logger.info( 'parsed result %s ...' % result ) 
        responses = [] # setup empty list
        p = '%Y %b %d %H:%M'
        epoch = datetime(1970, 1, 1)
        for f_c in result:
            response = {} # setup empty list
            mytime = '%s %s' % (f_c['date'], f_c['time'])
            _time = ((datetime.strptime(mytime, p) - epoch).total_seconds())
            response['_time'] = _time
            response['phase'] = f_c['phase']
            od = collections.OrderedDict(sorted(response.items())) # sort the list
            responses.append(od) # append the ordered results to the list
        splunk.Intersplunk.outputResults(responses) # print the result into Splunk UI

    # getting weather data
    if 'weather' in section_name:
        r_parsed = ''
        if forecast == "yes":
            con_str = '%s/data/2.5/forecast?lat=%s&lon=%s&units=metric&appid=%s&cnt=14' % (server,lat,lon,token)
        if forecast == "no":
            con_str = '%s/data/2.5/weather?lat=%s&lon=%s&units=metric&appid=%s&cnt=14' % (server,lat,lon,token)
        logger.info( 'using con_str %s ...' % con_str ) 
        url = urllib2.urlopen('%s' % con_str)
        r_parsed = json.loads(url.read())
        logger.info( 'parsed result %s ...' % r_parsed ) 
        responses = [] # setup empty list
        if forecast == "yes":
            result = r_parsed['list']
            for f_c in result:
                response = {} # setup empty list
                response['_time'] = f_c['dt'] # fill in key value pairs
                response['temp'] = f_c['main']['temp'] # fill in key value pairs
                response['pressure'] = f_c['main']['pressure'] # fill in key value pairs
                response['humidity'] = f_c['main']['humidity'] # fill in key value pairs
                response['weather.icon'] = f_c['weather'][0]['icon'] # fill in key value pairs
                response['weather.id'] = f_c['weather'][0]['id'] # fill in key value pairs
                response['weather.desc'] = f_c['weather'][0]['description'] # fill in key value pairs
                response['weather.main'] = f_c['weather'][0]['main'] # fill in key value pairs
                response['clouds'] = f_c['clouds']['all'] # fill in key value pairs
                response['wind.speed'] = f_c['wind']['speed'] # fill in key value pairs
                response['wind.deg'] = f_c['wind']['deg'] # fill in key value pairs
                od = collections.OrderedDict(sorted(response.items())) # sort the list
                responses.append(od) # append the ordered results to the list
            splunk.Intersplunk.outputResults( responses ) # print the result into Splunk UI
        if forecast == "no":
            f_c = r_parsed
            response = {} # setup empty list
            response['_time'] = f_c['dt'] # fill in key value pairs
            response['temp'] = f_c['main']['temp'] # fill in key value pairs
            response['pressure'] = f_c['main']['pressure'] # fill in key value pairs
            response['humidity'] = f_c['main']['humidity'] # fill in key value pairs
            response['weather.icon'] = f_c['weather'][0]['icon'] # fill in key value pairs
            response['weather.id'] = f_c['weather'][0]['id'] # fill in key value pairs
            response['weather.desc'] = f_c['weather'][0]['description'] # fill in key value pairs
            response['weather.main'] = f_c['weather'][0]['main'] # fill in key value pairs
            response['clouds'] = f_c['clouds']['all'] # fill in key value pairs
            response['wind.speed'] = f_c['wind']['speed'] # fill in key value pairs
            response['wind.deg'] = f_c['wind']['deg'] # fill in key value pairs
            od = collections.OrderedDict(sorted(response.items())) # sort the list
            responses.append(od) # append the ordered results to the list
            splunk.Intersplunk.outputResults( responses ) # print the result into Splunk UI

    # getting directions
    if 'direction' in section_name:
        con_str = '%sjson?origin=%s,%s&destination=%s,%s&units=metric&key=%s' % (server,lat,lon,dest_lat,dest_lon,token)
        logger.info( 'using con_str %s ...' % con_str ) 
        url = urllib2.urlopen('%s' % con_str)
        r_parsed = json.loads(url.read())
        result = r_parsed['routes']
        logger.info( 'parsed result %s ...' % result ) 
        responses = [] # setup empty list
        step_num = 0
        for route in result:
            for leg in route['legs']:
                for step in leg['steps']:
                    response = {} # setup empty list
                    response['step_num'] = step_num # fill in key value pairs
                    response['start.lat'] = step['start_location']['lat'] # fill in key value pairs
                    response['start.lon'] = step['start_location']['lng'] # fill in key value pairs
                    response['stop.lat'] = step['end_location']['lat'] # fill in key value pairs
                    response['stop.lon'] = step['end_location']['lng'] # fill in key value pairs
                    od = collections.OrderedDict(sorted(response.items())) # sort the list
                    responses.append(od) # append the ordered results to the list
                    step_num += 1
        splunk.Intersplunk.outputResults( responses ) # print the result into Splunk UI

except Exception, e: # get error back
    logger.error( 'ERROR: unable to get data.' ) 
    logger.error( 'ERROR: %s ' % e ) 
    splunk.Intersplunk.generateErrorResults(': %s' % e) # print the error into Splunk UI
    sys.exit() # exit on error
