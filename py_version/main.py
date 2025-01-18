import sys
import os
import subprocess

# Remember to write this name to the .gitignore file.
envName='venv'
essentialEnvPaths = { 'win32':  [ os.path.join(envName, 'Scripts', 'python.exe'),
                                  os.path.join(envName, 'Scripts', 'activate') ],
                      'linux':  [ os.path.join(envName, 'bin', 'python'),
                                  os.path.join(envName, 'bin', 'activate') ],
                      'darwin': [ os.path.join(envName, 'bin', 'python'),
                                  os.path.join(envName, 'bin', 'activate') ] }
currSys = sys.platform
currEssentialEnvPaths = essentialEnvPaths[currSys]



###############################################################################################



def checkIfAnyPathMissing():
    global currEssentialEnvPaths
    return any( (not os.path.exists(essPath))   for essPath in currEssentialEnvPaths )



def checkIfAnyDirInside():
    global envName
    doesEnvDirExist = os.path.exists(envName)
    return (not any( os.path.isdir(os.path.join(envName, entry))    for entry in os.listdir(envName)))   if doesEnvDirExist   else False



def createVirtualEnvIfNecessary(forceReinstall=False):
    global envName, currEssentialEnvPaths
        
    if forceReinstall   or   not os.path.exists(envName)   or   checkIfAnyPathMissing()   or   not checkIfAnyDirInside():
        
        msgText = f'\nCreating a new virtual enviroment in the directory "{envName}"'
        print(msgText + '...')

        try:
            # stdout=subprocess.PIPE: Captures the standard output (i.e., the data that the process would normally print to the screen).
            # stderr=subprocess.PIPE: Captures the standard error stream (i.e., the errors that the process would normally print to the screen).
            subprocess.check_call([sys.executable, '-m', 'venv', envName], stderr=subprocess.PIPE)

            if checkIfAnyPathMissing():
                import shutil
                shutil.rmtree(envName)
                print(f'\nHave to remove old {envName} directory.')
                setupEnvironment(True)
            
            print('Ends successfully.')
            return True

        except Exception as e:
            print(f'\nError while {msgText[0].upper() + msgText[1:]}: {e}')
            return False
        
    else:
        print(f'\nThe virtual environment "{envName}" already exists.')
    
    return True



###############################################################################################



def runVirtualEnv():
    global envName, currEssentialEnvPaths
    
    command = []

    if currSys == "win32":
        commandBefore = 'start cmd /K '
        commandMain = f'\"{currEssentialEnvPaths[1]}'

    elif currSys in ['linux', 'darwin']:
        commandBefore = 'bash -c '
        commandMain = f'\"source {currEssentialEnvPaths[1]}'
    
    try:
        if not checkIfAnyPathMissing()   or   checkIfAnyDirInside():
            command = commandBefore + commandMain + '   &&   python -c \"import main; main.main()\"   &&   deactivate   &&   exit\"'
            subprocess.check_call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f'\nThe virtual environment "{envName}" activated.')
            sys.exit()
            return True
        
        else:
            raise FileNotFoundError
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f'\nError while activating the virtual environment "{envName}".')
        setupEnvironment(True)
        return False



###############################################################################################



def doesPackageNeedInstallation(packageName='', requiredVer=''):
    global currEssentialEnvPaths
    try:
        
        envPythonPath = currEssentialEnvPaths[0]
        commandResult = subprocess.check_output([envPythonPath, '-m', 'pip', 'show', packageName], stderr=subprocess.PIPE).decode('utf-8')
        installedVer = None

        for line in commandResult.splitlines():
            if line.startswith('Version:'):
                installedVer = line.split(':')[1].strip()
                break
        
        return not (installedVer == requiredVer)
    
    except subprocess.CalledProcessError:
        return True
    
    except FileNotFoundError:
        print(f'\nFile {envPythonPath} not found.')
        setupEnvironment(True)



def installRequirements(requirementsFile='requirements.txt'):
    global envName, currEssentialEnvPaths

    packagesToInstall=[]

    try:
        with open(requirementsFile, 'r') as file:
            
            for line in file:
                packageLine = line.strip().split('==')
                packageName = packageLine[0]
                packageVer = packageLine[1]

                if packageName   and   doesPackageNeedInstallation(packageName, packageVer):
                    packagesToInstall.append(packageName)
            
            if len(packagesToInstall):
                raise ImportError


    except ImportError as e:
        print(f'\nSome requirements need to be installed: {packagesToInstall}')
        for packageName in packagesToInstall:
            envPythonPath = currEssentialEnvPaths[0]
            try:
                subprocess.check_call([envPythonPath, '-m', 'pip', 'install', packageName], stderr=subprocess.PIPE)
            
            except subprocess.CalledProcessError:
                print('\nError while installing requirements.')
                setupEnvironment(True)

    except FileNotFoundError:
        print(f'\nFile {requirementsFile} not found.')
        return False


    else:
        print('\nAll of the requirements already exist.')

    return True



###############################################################################################



def addToSysPath(basePath='', innerFolderName=''):
    folderPathToAdd = ( basePath  if    not innerFolderName
                                  else  basePath / innerFolderName)

    if not folderPathToAdd.exists():
        print(f'\nThe directory "{folderPathToAdd}" does not exist.')
        sys.exit()

    else:
        sys.path.append(str(folderPathToAdd))
        return True



def addAllOfTheProjectFolders():
    from pathlib import Path
    
    projectRoot = Path(__file__).resolve().parent
    srcFolder = projectRoot / 'src'

    folderList = [ 'constants', 'handlers', 'logs', 'schedules', 'utils' ]
        
    for folderName in folderList:
        addToSysPath(srcFolder, folderName)
    
    return True



###############################################################################################



def setupEnvironment(forceReinstall=False, requirementsFile='requirements.txt'):
    if forceReinstall:
        print('\nReinstall environment.')
    
    try:
        noErrors = createVirtualEnvIfNecessary(forceReinstall)
        if noErrors:
            noErrors = installRequirements(requirementsFile)
            
        if forceReinstall:
            runVirtualEnv()
        
    except Exception as e:
        print(f'\nError: {e}')
        sys.exit()



###############################################################################################



def main():
    if addAllOfTheProjectFolders():
    
        from src import ( getClassesDataFromSchoolWebPage,
                          loadClassesDataVariables, createOrEditMainExcelFile, getClassesDataDfs,
                          createOtherScheduleExcelFiles,
                          openScheduleFilesWithDefApps )
        
        #turnOffFutureWarnings()

        classesData = getClassesDataFromSchoolWebPage()

        if classesData:
            loadClassesDataVariables(classesData)
            createOrEditMainExcelFile()
            createOtherScheduleExcelFiles(getClassesDataDfs())
            openScheduleFilesWithDefApps()



if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', action='store_true', help='Run the configuration or add the missing modules.')
    args = parser.parse_args()

    if args.setup:
        setupEnvironment()

    try:
        runVirtualEnv()
        
    except Exception as e:
        print(f'\nError: {e}\nTry command:\n\npython main.py --setup')