from constants import scheduleExcelPath, excelEngineName, scheduleExcelJSONPath, scheduleDfsJSONPath, scheduleJSONPath
from utils import convertToObjOfDfs, convertObjOfDfsToJSON, createDraftSheetIfNecessary, convertCurrExcelToDfsJSON, writeObjOfDfsToExcel, delDraftIfNecessary, compareAndUpdateFile, autoFormatExcelFile
#, colLetterToNr
import json
from pandas import ExcelWriter


classesDataJSON = ''
classesDataDfs = None
classesDataDfsJSON = ''


def loadClassesDataVariables(classesData):
    
    global classesDataJSON, classesDataDfs, classesDataDfsJSON

    classesDataJSON = json.dumps(classesData, indent=4)
    classesDataDfs = convertToObjOfDfs(classesData)
    classesDataDfsJSON = convertObjOfDfsToJSON(classesDataDfs)


def createOrEditExcelFile():
    
    global classesDataJSON, classesDataDfs, classesDataDfsJSON

    createDraftSheetIfNecessary()

    currExcelAsJSON = convertCurrExcelToDfsJSON()

    try:
        
        if not (currExcelAsJSON == classesDataDfsJSON):
            with ExcelWriter(scheduleExcelPath, mode='w+', engine=excelEngineName) as writer:
                
                try:
                    writeObjOfDfsToExcel(writer, classesDataDfs)
                    #print('currExcelAsJSON', currExcelAsJSON)
                    #print('classesDataDfsJSON', classesDataDfsJSON)
                    currExcelAsJSON = classesDataDfsJSON


                except Exception as writeError:
                    print(f"Error while writing to Excel file: {writeError}")

        else:
            print('Nothing to be updated in Excel file.')

        try:
            delDraftIfNecessary()

        except Exception as draftError:
            print(f"Error while deleting the draft sheet: {draftError}")


    except Exception as e: 
        print(f"Error while handling the Excel file: {e}")


    # to avoid issues, compare file contents
    # & update if it's neccessarry
    if(compareAndUpdateFile(scheduleExcelJSONPath, currExcelAsJSON)):
        autoFormatExcelFile()
    compareAndUpdateFile(scheduleDfsJSONPath, classesDataDfsJSON)
    compareAndUpdateFile(scheduleJSONPath, classesDataJSON)