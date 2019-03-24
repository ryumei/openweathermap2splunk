#!/bin/sh

cd /opt/local/openweathermap2splunk
. env/bin/activate
python openweathermap2splunk.py -c openweathermap2splunk.conf

