# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
from piston.utils import FormValidationError

"""Ecov Lib Exceptions

"""

class LibException(Exception):
    """Base lib exception; All exceptions of the module inherits this one.
    
    """
    pass

# does not exists
class CityDoesNotExist(LibException):
    pass
     
class TripDoesNotExist(LibException):
    pass    

class TalkDoesNotExist(LibException):
    pass

# already exists
class MarkAlreadyExists(LibException):
    pass

class TalkAlreadyExists(LibException):
    pass

#invalid data
class InvalidTripType(LibException):
    pass    
    
class InvalidGeometry(LibException):
    pass  
    
class InvalidUser(LibException):
    pass      
    
class InvalidMail(LibException):
    pass

#invalid forms
class InvalidTripForm(FormValidationError):
    pass
    
class InvalidTripDemandForm(FormValidationError):
    pass

class InvalidTripDemandForm(FormValidationError):
    pass
       
class InvalidReportForm(FormValidationError):
    pass
    
class InvalidContactUserForm(FormValidationError):
    pass
    
#others

class TempReportIsntOpen(LibException):
    pass
