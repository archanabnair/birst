import os
from sys import version_info
import importlib
from pip._internal import main
import logging 
import sys
from datetime import datetime

def log_file_init(supplied_path): 
	try:
		if not os.path.exists(supplied_path):
			os.makedirs(supplied_path)
		os.chdir(supplied_path)
		# Creating name of log file with format log_YYYY-MM-DD_HH-MM.log

		print("supplied path is: ",supplied_path)
		print("creating log file name")
		now = datetime.now()
		str_now=now.strftime("%Y-%m-%d_%H-%M-%S")
		file_name='setup_log_'+str_now+'.log'

		# Configuring the log file
		logging.basicConfig(
		filename=file_name,
		level=logging.DEBUG,
		format='%(asctime)s %(levelname)s: %(message)s',
		datefmt='%m/%d/%Y %I:%M:%S %p')

		# Leave STDOUT as Listener
		root_log=logging.getLogger()
		root_log.setLevel(logging.INFO)
		scr=logging.StreamHandler(sys.stdout)
		scr.setLevel(logging.INFO)
		formatter=logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
		formatter.datefmt = '%m%d%Y %Y:%M:%S %p'
		scr.setFormatter(formatter)
		root_log.addHandler(scr)

		return file_name
	except Exception as e:
		print(e)
def install_and_import(package):
    
    try:
        importlib.import_module(package)
        logging.info("Succesfully imported package: %s ",package)
    except ImportError:
        
        logging.info("No module named %s",package)
        main(['install', package])

    finally:
        globals()[package] = importlib.import_module(package)
        logging.info('Successfully installed package: %s',package)


def check_python_version():
	try: 
		logging.info("Python Version: %s",str(version_info[0])+'.'+str(version_info[1])+'.'+str(version_info[2]))
		version=str(version_info[0])+'.'+str(version_info[1])
		print("version is...",version)
		if float(version) < 3.6:
			logging.error("Python version needs an upgrade. Please upgrade to the required version and retry Setup",exc_info='True')
			sys.exit(1)
		else:
			logging.info("Python version meets requirement.")
			return str(version_info[0])+'.'+str(version_info[1])+'.'+str(version_info[2])
		
	except  Exception as e:
		logging.info("Exception occured: %s",e) 


def create_dir(path):
	try:
		if not os.path.exists(path):
				os.makedirs(path)
	except  Exception as e:
		logging.info("Exception occured: %s",e) 

current_file_dir=os.path.dirname(os.path.realpath(__file__))

		

logfiledir=current_file_dir+"\logs\\"
logfilename=log_file_init(logfiledir)
logging.info("---Log File Created---")
logging.info("Current File is located in: %s ",current_file_dir)
logging.info("Log file name: %s",current_file_dir+"\logs\\"+logfilename)

logging.info("---Checking Python version---")
python_version_info=check_python_version()
logging.info("Python version info: %s",python_version_info)
logging.info("---Python version satisfies requirement---")

logging.info("---Creating Required Directories---")
create_dir(current_file_dir+'\BirstConnect')
logging.info("Directory Created: "+current_file_dir+'\BirstConnect')
logging.info("---Required Directories successfully created---")

logging.info("---Installing required Python packages---")
install_and_import('boto3')
install_and_import('configparser')
install_and_import('io')
install_and_import('logging')
install_and_import('os')
install_and_import('shutil')
install_and_import('smtplib')
install_and_import('time')
install_and_import('zeep')
install_and_import('subprocess')
install_and_import('email')
logging.info("---Successfully Installed required Python packages---")

logging.info("Set up Complete.")


