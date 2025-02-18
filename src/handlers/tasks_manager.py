from src.handlers.schedules_scraper import getClassesDataFromSchoolWebPage
from src.handlers.scraper_saver import loadClassesDataVariables, createOrEditMainExcelFile
from src.handlers.schedules_creator import createScheduleExcelFiles
from src.handlers.files_opener import openScheduleFilesWithDefApps, openOverviewFilesWithDefApps
from src.handlers.overviews_creator import createScheduleOverviews
from src.constants.scraper_constants import schoolsWebInfo



def scrapeSchoolWebs():
    
    for schoolWebInfo in [schoolsWebInfo['lojagiellonczyk']]:

        classesData = getClassesDataFromSchoolWebPage(schoolWebInfo)

        if classesData:
            loadClassesDataVariables(classesData)
            classesDataDfs = createOrEditMainExcelFile(schoolWebInfo)
            globalSchedules = createScheduleExcelFiles(classesDataDfs, schoolWebInfo)
            createScheduleOverviews(globalSchedules, schoolWebInfo)
            #openScheduleFilesWithDefApps()
            #openOverviewFilesWithDefApps()
