from django.test import _doctest as doctest
from django.test.testcases import OutputChecker, DocTestRunner
from django.core.management import call_command
from bv.server.lib import libcarpool

def suite():
    loader = DoctestLoader()
    return loader.load_module_doctests(libcarpool)

class DoctestLoader:
    """Provides a common way to load doctests from different sources
    
    """
    def load_fixtures(self, fixtures):
        """Load the given list of fixtures
        """
        call_command('loaddata', *fixtures, **{'verbosity': 1})
    
    def load_module_doctests(self, module):
        """Load the doctests for the specified module.
        
        Check if a __fixtures__ param exists within the module, and load 
        fixtures if defined.
        """
        self.load_fixtures(module.__fixtures__)
        return doctest.DocTestSuite(module, checker=OutputChecker(), runner=DocTestRunner)
