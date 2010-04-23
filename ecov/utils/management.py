# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import logging
import datetime
import os
import sys
from optparse import make_option

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand as DefaultBaseCommand

class BaseCommand(DefaultBaseCommand):
    """Parent class for all commands. provide useful tools to commands"""

    option_list = DefaultBaseCommand.option_list + (
        make_option('--loggername', dest='logger_name',
            help='Set the name of the logger instance'),
        make_option('--scriptname', dest='script_name',
            help='Set the name of the script (for logging)'),
    )
       
    def __init__(self):
        self.script_name = 'default_script'
        self.logger_name = 'default_logger'
     
    def init_logger(self, options):
        """Init the cron script logger"""
        return LogWithSettings(logger_name=self.get_option(options, 'logger_name', self.logger_name), 
            script_name=self.get_option(options, 'script_name', self.script_name))

    def get_absolute_url(self):
        """Return the absolute URL (base) for active site"""
        absolute_url = settings.PROJECT_ROOT_URL
        if absolute_url.endswith('/'):
            absolute_url = absolute_url.strip('/')
        return absolute_url
        
    def get_option(self, options, name, default):
        """
        TODO Use options.get instead ?!
        Return an option value, or default value
        """
        value = options.get('logger_name')
        if(value == None):
            value = default
            
        return value
    
class LogWithSettings:
    """ 
    Simple helper to log all cron scripts.
    
    Log information in the right log file, and create path and files if needed
    """
    def __init__(self, logger_name='', script_name=''):
        
        self.log_path = settings.SCRIPTS_LOG_PATH
        self.log_instance_name = settings.SCRIPTS_LOG_PREFIX
        self.script_name = script_name
        self.get_logger(logger_name)
        self.filename = '%s_%s.log' % (self.log_instance_name, self.script_name)
        self.fullpath = os.path.join(
            self.log_path, self.get_today().year.__str__(), 
            self.get_today().month.__str__(), 
            self.get_today().day.__str__(), 
            self.filename)
            
        if not os.path.isdir(os.path.split(self.fullpath)[0]):
            os.makedirs(os.path.split(self.fullpath)[0])
            
        logging.basicConfig(
            level=logging.DEBUG, 
            format='%(asctime)s %(levelname)s %(message)s',
            filename=self.fullpath)
    
    def get_logger(self, logger_name=''):
        """create the logger instance and return it"""
        if logger_name:
            self.log_name = logger_name
            self.logger = logging.getLogger(self.log_name)
        else:
            self.logger = logging.getLogger()
        return self.logger
            
    def get_today(self):
        """return the date of today"""
        return datetime.date.today()
    
    def error_log(self, err):
        """log an error"""
        self.logger.error(err)
        
    def info_log(self, msg):
        """log an information"""
        self.logger.info(msg)        
