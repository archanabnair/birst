import configparser     # Configuration file parser
import datetime         # Enables date functions
import io
import logging          # Log file management
import math
import os               # system functions
import re               # Regex functions
import sys
import time             # Sleep function
import zeep             # Client interaction for Birst Web services
from datetime import datetime       # Date functions 
from subprocess import Popen,PIPE   # Enables access to system commands. Spawn processes, connect to I/O or error pipes, get return codes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import COMMASPACE, formatdate


class automation_controller(object):
    @staticmethod
    
    def log_file_init(supplied_path): 
        
        # Set CWD for log file creation
        os.chdir(supplied_path)

        # Creating name of log file with format log_YYYY-MM-DD_HH-MM.log
        now = datetime.now()
        str_now=now.strftime("%Y-%m-%d_%H-%M-%S")
        file_name='log_'+str_now+'.log'

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
    def addUser(self,url,birst_username, birst_password,birst_space,birst_space_name,add_username,password,email):
            logging.info('---------------Creating User in Birst---------------')
            wsdl = url
            client = zeep.Client(wsdl=wsdl)
            loginToken = client.service.Login(birst_username,birst_password)
            logging.info('Login Successful!. Token ID is %s',loginToken)
            logging.info('Creating User %s in Birst',add_username)
            client.service.addUser(loginToken,birst_username,birst_space,password,email)
            client.service.Logout(loginToken)
            logging.info("User %s created in Birst %s",add_username,birst_space_name)
    def addUserToSpace(self,url,birst_username, birst_password,spaceId,birst_space_name,username,add_as_admin):
            logging.info('---------------Adding User to Space---------------')
            wsdl = url
            client = zeep.Client(wsdl=wsdl)
            loginToken = client.service.Login(birst_username,birst_password)
            logging.info('Login Successful!. Token ID is %s',loginToken)
            logging.info('Adding User %s to Space: %s',username,birst_space_name)
            client.service.addUserToSpace(loginToken,username,spaceId,add_as_admin)
            client.service.Logout(loginToken)
            logging.info("User %s added to space %s",username,birst_space_name)

    def addGroupToSpace(self,url,birst_username, birst_password,spaceId,birst_space_name,group_name):
            logging.info('---------------Adding Group to Space---------------')
            wsdl = url
            client = zeep.Client(wsdl=wsdl)
            loginToken = client.service.Login(birst_username,birst_password)
            logging.info('Login Successful!. Token ID is %s',loginToken)
            logging.info('Adding Group %s to Space: %s',group_name,birst_space_name)
            client.service.addGroupToSpace(loginToken,group_name,spaceId)
            client.service.Logout(loginToken)
            logging.info("Group %s added to space %s",group_name,birst_space_name)

    def addUserToGroupInSpace(self,url,birst_username, birst_password,spaceId,birst_space_name,group_name,username):
            logging.info('---------------Adding User to Group in Space---------------')
            wsdl = url
            client = zeep.Client(wsdl=wsdl)
            loginToken = client.service.Login(birst_username,birst_password)
            logging.info('Login Successful!. Token ID is %s',loginToken)
            logging.info('Adding User %s to Group %s in Space: %s',username,group_name,birst_space_name)
            client.service.addUserToGroupInSpace(loginToken,username,group_name,spaceId)
            client.service.Logout(loginToken)
            logging.info("User %s added to Group %s in space %s",username,group_name,birst_space_name)

    def addAclToGroupInSpace(self,url,birst_username, birst_password,spaceId,birst_space_name,group_name,ACL):
            logging.info('---------------Adding ACL to Group in Space---------------')
            wsdl = url
            client = zeep.Client(wsdl=wsdl)
            loginToken = client.service.Login(birst_username,birst_password)
            logging.info('Login Successful!. Token ID is %s',loginToken)
            logging.info('Adding ACL %s to Group %s in Space: %s',ACL,group_name,birst_space_name)
            client.service.addAclToGroupInSpace(loginToken,group_name,ACL,spaceId)
            client.service.Logout(loginToken)
            logging.info("ACL %s added to Group %s in space %s",ACL,group_name,birst_space_name)
 
if __name__ == "__main__":
    arg_list=str(sys.argv)
    root_dir=sys.argv[1]
    try:
        #0 Configure Log File and variables 
            os.chdir(root_dir)
            now = datetime.now()
            config = configparser.ConfigParser()  #instantiate
            config.read('config_auth.ini') #parse config file
            log_file_location=config.get('default','log_file')
            log_filename=automation_controller().log_file_init(log_file_location)
            logging.info('Job started at:%s',now)
            start=now   #Enhanced logging

            # Notify
            sender_email=config.get('notify','sender_email')
            sender_password=config.get('notify','sender_password')
            recipient_list=config.get('notify','recipient_email')

            # Birst Space: SDM Raw Data
            url=config.get('connections.birst_sdm_raw_data_pipeline_test','url')
            birst_username=config.get('connections.birst_sdm_raw_data_pipeline_test','username')
            birst_password=config.get('connections.birst_sdm_raw_data_pipeline_test','password')
            birst_space_name=config.get('connections.birst_sdm_raw_data_pipeline_test','spacename')
            birst_space=config.get('connections.birst_sdm_raw_data_pipeline_test','spaceID')
      
    except configparser.NoSectionError as se:
            logging.error(se)
    except configparser.NoOptionError as oe:
            logging.error(oe)
    except IOError as io:
            logging.error(io)
    except OSError as ose:
            logging.error(ose)
    except Exception as e:
            logging.error(e)
        
    #add_username
    password='foo'
    email='foo@bar.com'
    #add_as_admin='y'
    group_name='Admin_automation'
    ACL='Visualizer'
    if sys.argv[2]=='addUserToSpace':
            add_username=sys.argv[3]
            add_as_admin=sys.argv[4]
            automation_controller().addUserToSpace(url,birst_username, birst_password,birst_space,birst_space_name,add_username,add_as_admin)
    if sys.argv[2]=='addUser':
        add_username=sys.argv[3]
        password=sys.argv[4]
        email=sys.argv[5]
        automation_controller().addUser(url,birst_username, birst_password,birst_space,birst_space_name,add_username,password,email)
    if sys.argv[2]=='addGroupToSpace':
        group_name=sys.argv[3]
        automation_controller().addGroupToSpace(url,birst_username, birst_password,birst_space,birst_space_name,group_name)
    if sys.argv[2]=='addUserToGroupInSpace':
        group_name=sys.argv[3]
        add_username=sys.argv[4]
        automation_controller().addUserToGroupInSpace(url,birst_username, birst_password,birst_space,birst_space_name,group_name,add_username)

    if sys.argv[2]=='addAclToGroupInSpace':
        group_name=sys.argv[3]
        ACL=sys.argv[4] # Visualizer,ExploreInVisualizer,EditDashboard'
        automation_controller().addAclToGroupInSpace(url,birst_username, birst_password,birst_space,birst_space_name,group_name,ACL)

