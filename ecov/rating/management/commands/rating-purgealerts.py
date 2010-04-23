# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

from utils.management import BaseCommand
from rating.models import TempReport

class Command(BaseCommand):
    help = """Fetch all closed temp evaluations, transform them in real 
    evaluations and delete the temp ones.
    """
    
    def __init__(self):
        BaseCommand.__init__(self)
        self.script_name = 'purge-rating-alerts'
    
    def handle(self, *args, **options):    
        purge_logger = self.init_logger(options)
        
        purge_logger.info_log("START run_purge")
        tempreports = TempReport.objects.get_closed_tempreports()

        nb_reports_ok = 0
        nb_reports_error = 0
        nb_reports_created = 0
        for report in tempreports:
            try:
                nb_reports_created += report.transform(both_reports=False)
                nb_reports_ok += 1
            except Exception, err:
                nb_reports_error += 1
                purge_logger.error_log("error: %s\n" % err)

        purge_logger.info_log("%d reports created" % nb_reports_created)
        purge_logger.info_log("%d temp reports successfully treated" % nb_reports_ok)
        purge_logger.info_log("%d temp reports in error" % nb_reports_error)
        purge_logger.info_log("END run_purge")    
