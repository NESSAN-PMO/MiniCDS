#!/usr/bin/env python

from __future__ import unicode_literals
from future.standard_library import install_aliases
install_aliases()
from builtins import bytes

import time
import http.server
import os, sys, os.path
from urllib.parse import parse_qs,urlparse
from socketserver import ThreadingMixIn
import threading
from math import sqrt
import re
from astropy import log

from .config import *
cfg=dict(config.items("DEFAULT"))

log.setLevel( "DEBUG" )
try:
    HOST_NAME = cfg['host'] 
except:
    HOST_NAME = ''

PORT_NUMBER = int(cfg['server_port']) # Maybe set this to 9000.

def UCAC4Cat( ra,dec,r,magmin,magmax,maxstars ):

    from refcat import UCAC4
        
    try:
        cfg = dict( config.items("UCAC4") )
        cat = UCAC4( path = cfg['datadir'] )
    except:
        cat = UCAC4() 
    if not cat.valid:
        log.error( "UCAC-4 local copy is not valid now." )
        return "UCAC-4 local copy is not valid now."
    cat.extract_ucac4_stars( ra, dec, r*2, r*2 )

    log.debug("RA/DEC/r: {:f} {:f} {:f}, MIN/MAX MAG: {:f} {:f}, MAXSTARS: {:d}".format(ra,dec,r,magmin,magmax,maxstars))
    if magmin != 99 or magmax != -99:
        data=cat.data[(cat.data['mag1']<=magmin) & (cat.data['mag1']>=magmax)]
    else:
        data = cat.data
    data.sort( 'mag1' )
    data = data[:maxstars]
    '''
    Special output to mimic CDS Strasbourg server output
    as need by scamp refcatlog.
    '''
    lines = []
    lines.append( "#======== UCAC4 server (2017-06-05, V0.1) ======== PMO mini CDS, Nanjing ========" )
    lines.append( "#Center: {:8.4f} {:8.4f}".format( ra, dec ) )
    lines.append( "#UCAC4    |    RA  (ICRS) Dec     +/- +/-  mas  EpRA    EpDE  | f.mag  a.mag  +/- |of db| Na  Nu  Cu| pmRA(mas/yr)pmDE  +/-  +/-|MPOS1      UCAC2      Tycho-2    |     2Mkey   Jmag  +/-:cq   Hmag  +/-:cq   Kmag  +/-:cq|  Bmag:1s.   Vmag:1s.   gmag:1s.   rmag:1s.   imag:1s.|gc.HAbhZBLNS|LED 2MX|;     r(\")" )
    t1=time.time()
    for r in data:
        mas = int( sqrt( r[7] ** 2 + r[8] ** 2 ) )
        #apass mag sigma
        asb = ("%3.2f"%r[33])[-3:] if r[33] >= 0 else '-'+("%3.2f"%r[33])[-2:]
        asv = ("%3.2f"%r[34])[-3:] if r[34] >= 0 else '-'+("%3.2f"%r[34])[-2:]
        asg = ("%3.2f"%r[35])[-3:] if r[35] >= 0 else '-'+("%3.2f"%r[35])[-2:]
        asr = ("%3.2f"%r[36])[-3:] if r[36] >= 0 else '-'+("%3.2f"%r[36])[-2:]
        asi = ("%3.2f"%r[37])[-3:] if r[37] >= 0 else '-'+("%3.2f"%r[37])[-2:]
        line = []
        line.append("{:03d}-{:06d}".format(r[45], r[46]))
        line.append("{:011.7f}{:+011.7f}{:4d}{:4d}{:5d}{:8.2f}{:8.2f}"
                .format(r[0],r[1],r[7],r[8],mas,r[12],r[13]))
        line.append("{:6.3f} {:6.3f} {:4.2f} ".format(r[2],r[3],r[4]))
        line.append("{:2d}{:3d}".format(r[5],r[6]))
        line.append("{:3d} {:3d} {:3d}".format(r[9],r[10],r[11]))
        line.append("{:+8.1f} {:+8.1f} {:4.1f} {:4.1f}".format(r[14],r[15],r[16],r[17]))
        line.append("{:09d} {:03d}-{:06d}             ".format(r[42],r[43],r[44]))
        line.append("{:10d} {:6.3f} {:4.2f}:{:02d} {:6.3f} {:4.2f}:{:02d} {:6.3f} {:4.2f}:{:02d}".format(r[18],r[19],r[25],r[22],r[20],r[26],r[23],r[21],r[27],r[24]))
        line.append("{:6.3f}:{:s} {:6.3f}:{:s} {:6.3f}:{:s} {:6.3f}:{:s} {:6.3f}:{:s}".format(r[28],asb,r[29],asv,r[30],asg,r[31],asr,r[32],asi))
        line.append("{:02d}.{:09d}".format(r[38],r[39]))
        line.append("{:3d} {:3d}".format(r[40],r[41]))
        line.append(";")
        lines.append( "|".join( line ) )

    log.info( "Using {:f} s".format( time.time() - t1 ) )
    lines.append("")
    out = '\n'.join( lines )

    return out

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        services_cmd={'help':self.help,'viz-bin/aserver.cgi':self.minicds}
        service=urlparse(self.path).path[1:]
        qs = parse_qs(urlparse(self.path).query)
        services=list(services_cmd.keys())
        if service not in services:
            services_cmd['help'](qs)
            return
        if service=='viz-bin/aserver.cgi':
            #Special handler to mimic UCAC4 vizier server import re
            log.debug("VIZ:{:s}".format(urlparse(self.path).query))
            response=services_cmd[service](urlparse(self.path).query)
        else:
            response=services_cmd[service](qs)

    def help(self,params):
        self.send_response(200)
        self.send_header("Content-type", "text/text")
        self.end_headers()
        selfpath = os.path.dirname( __file__ )
        with open( os.path.join( selfpath, 'data', 'helptext.txt' ),'r' ) as f:
            data=f.read()
        self.wfile.write(bytes(data,"utf-8"))

    def minicds(self,params):
        log.debug(params)	
        params=params.split('&')
        log.debug(params)	

        magmin = 99
        magmax = -99
        for i in range( len( params ) ):
            if params[i] == '-c':
                if params[i+1].find('%2b')>=0 or params[i+1].find('+') >=0:
                    sep='%2b|%2b|\+'		
                    sig=1
                elif params[i+1].find('%2d') >=0 or params[i+1].find('-') >=0:
                    sep='%2d|%2D|\-'
                    sig=-1
                elif params[i+1].find('%20')>=0 or params[i+1].find(' ') >=0:
                    sep='%20| '
                    sig=1

                #ra=float(params[i+1].split(sep)[0])
                #dec=sig*float(params[i+1].split(sep)[1])

                radec=re.split(sep,params[i+1].strip())
                ra=float(radec[0])
                dec=sig*float(radec[1])
                continue

            elif params[i] == '-r':
                r=float(params[i+1])/60.
                continue

            elif params[i] == '-lmr':
                limits=params[i+1].split(',')
                magmin=int(float(limits[1]))
                magmax=int(float(limits[0]))
                continue
            elif params[i] == '-m':
                maxstars=int(params[i+1])
                continue
            else:
                pass

        if params[0] == 'ucac4':
            self.sendOutput( UCAC4Cat( ra, dec, r, magmin, magmax, maxstars ) )

    def sendOutput(self,data):
        self.send_response(200)

        size=len(data)	
        self.send_header("Content-Length",str(size))
        contentType="text/text"

        self.send_header("Content-type",contentType)
        self.end_headers()
        log.debug("START SENDING {:d}".format(size))
        self.wfile.write(bytes(data,"utf-8"))
        log.debug("END SENDING.")

class ThreadedHTTPServer(ThreadingMixIn,http.server.HTTPServer):
    """Handle requests in a separate thread."""

def main():
    #server_class = BaseHTTPServer.HTTPServer
    server_class = ThreadedHTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    httpd.daemon=True	
    log.info( "{:s} Server Starts - {:s}:{:d}".format(time.asctime(), HOST_NAME, PORT_NUMBER))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    log.info("{:s} Server Stops - {:s}:{:d}".format(time.asctime(), HOST_NAME, PORT_NUMBER))
