#*********************************************************************************************************************************
# Title: Pipeline orchestrator Script
# Author: Archana Balachandran
# Date: 2018-08-01
#
# Description: The script orchestrates the various activities in the data pipeline.
#              The various pipeline activities include:
#               1. Perform file count validation. Exit on Failure.
#               2. Execute the Birst Connect JNLP tasks to upload the files to Birst
#               3. Process Data in Birst 
#               4. Notify users upon pipeline completion
#                
#*********************************************************************************************************************************

import configparser     # Configuration file parser
import datetime         # Enables date functions
import fnmatch          # Text pattern matching
import io
import logging          # Log file management
import math
import os               # system functions
import re               # Regex functions
import shutil           # File System functions (copy, remove file)
import smtplib          # Email for notifications
import stat
import sys              # Exit and stdout functions
import time             # Sleep function
from datetime import datetime       # Date functions 
from subprocess import Popen,PIPE   # Enables access to system commands. Spawn processes, connect to I/O or error pipes, get return codes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import COMMASPACE, formatdate
import zeep


class automation_controller(object):
    #@staticmethod

    def __init__(self,root_dir):
        self.root_dir=root_dir
        try:
            #0 Configure Log File and variables 
            os.chdir(root_dir)
            now = datetime.now()
            self.start=now   #Enhanced logging
            config = configparser.ConfigParser()  #instantiate
            config.read('config_auth.ini') #parse config file
            self.log_file_location=config.get('default','log_file')
            self.log_file_name=self.log_file_init(self.log_file_location)
            logging.info('Job started at:%s',now)
           
                         
            # global
            self.cwd=config.get('default','cwd')


            # Notify
            self.sender_email=config.get('notify','sender_email')
            self.sender_password=config.get('notify','sender_password')
            self.recipient_list=config.get('notify','recipient_email')
            self.dev_recipient_list=config.get('notify','dev_recipient_list')
            self.smtp_host=config.get('notify','smtp_host')
            self.smtp_port=config.get('notify','smtp_port')

            # Decryption
            self.priv_key_dir=config.get('credentials.pgp','priv_key_dir')
            self.passphrase=config.get('credentials.pgp','passphrase')

            # preprocessing
            self.stg_dir=config.get('preprocessing','stg_dir') # local source directory for staging data
            self.process_dir=config.get('preprocessing','process_dir') 
            self.target_dir=config.get('preprocessing','target_dir') # local destination directory for birst pickup
            self.expected_file_count=config.get('preprocessing','expected_file_count')
            self.expected_file_list=config.get('preprocessing','expected_file_list')
            
            # Birst: Common variables
            self.birst_status_poll_timer=config.get('connections.birst_common','birst_status_poll_timer')
            self.publish_data_poll_timer=config.get('connections.birst_common','publish_data_poll_timer')
            self.max_poll_retries=config.get('connections.birst_common','max_poll_retries')
            self.publishdata_status_polling_timer=config.get('connections.birst_common','publishdata_status_polling_timer')
            self.load_status_polling_timer=config.get('connections.birst_common','load_status_polling_timer')
            
            # Birst Space: SDM Raw Data
            self.birst_url=config.get('connections.birst_sdm_raw_data','url')
            self.birst_username=config.get('connections.birst_sdm_raw_data','username')
            self.birst_password=config.get('connections.birst_sdm_raw_data','password')
            self.birst_space_name=config.get('connections.birst_sdm_raw_data','spacename')
            self.birst_space=config.get('connections.birst_sdm_raw_data','spaceID')
            self.birst_cmd_dir=config.get('connections.birst_sdm_raw_data','cmd_dir')
            self.processingGroups=config.get('connections.birst_sdm_raw_data','processingGroups')
            self.birst_connect_task=config.get('connections.birst_sdm_raw_data','birst_connect_task')
            


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

    def log_file_init(self,supplied_path): 
        
        # Set CWD for log file creation
        os.chdir(supplied_path)
        

        # Creating name of log file with format log_YYYY-MM-DD_HH-MM.log
        now = datetime.now()
        str_now=now.strftime("%Y-%m-%d_%H-%M-%S")
        log_file_name='log_'+str_now+'.log'

        # Configuring the log file
        logging.basicConfig(
        filename=log_file_name,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    
        # Leave STDOUT as Listener
        root_log=logging.getLogger()
        root_log.setLevel(logging.INFO)
        scr=logging.StreamHandler(sys.stdout)
        scr.setLevel(logging.INFO)
        formatter=logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        formatter.datefmt = '%m%d%Y %I:%M:%S %p'
        scr.setFormatter(formatter)
        root_log.addHandler(scr)
        
        return log_file_name

    def notify_users(self,msgtype,attach,user_type):

        # Define module variables
        sender_email=self.sender_email
        sender_password=self.sender_password
        recipient_email=self.recipient_list
        dev_recipient_list= self.dev_recipient_list
        smtp_host=self.smtp_host
        smtp_port=self.smtp_port

        log_file_location=self.log_file_location
        port=int(smtp_port)

        # Define Recipient list based on type of notifications - Developer vs Regular User
        if user_type=='dev':
            email_send=dev_recipient_list
            email_send_list=dev_recipient_list.split(',')
            subject = '[Developer Notification] SDM Automation Pipeline '
        if user_type=='user':
            email_send=recipient_email # get recipient list
            email_send_list=recipient_email.split(',') # get recipient list
            subject = 'SDM Automation Pipeline Notification'

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email_send
        msg['Subject'] = subject

        # Define Email Message
        if msgtype == 'Error':
            body = 'Hi \nThe pipeline has encountered an error and was terminated with status code 1. Refer log for details.\n\nBirst Automation Team'
        elif msgtype == 'Success': 
            body = 'Hi \nThe pipeline was executed successfully. Check attached log for details. \n\nBirst Automation Team'
        elif msgtype == 'Trigger file not found':
            body = 'Hi \nThe trigger file was not found in the MFT Inbox location after 3 retries. Please contact Axway for file receipt status. \n\nBirst Automation Team'
        else:
            body=msgtype
        msg.attach(MIMEText(body,'plain'))

        # Optional attachment block
        if attach=='T':
            filename=log_file_location+'\\'+self.log_file_name
            attachment_name=self.log_file_name
            attachment  =open(filename,'rb')
            part = MIMEBase('application','octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',"attachment; filename= "+attachment_name)
            msg.attach(part)

        text = msg.as_string()
        server = smtplib.SMTP(smtp_host,port)

        server.starttls() # Required for port 587 on SMTP server. Enables encryption and  upgrades an existing insecure connection to a secure connection using SSL/TLS
        
        server.login(sender_email,sender_password)
        #server.set_debuglevel(1)
        server.sendmail(sender_email,email_send_list,text)

        server.quit()
        
    

          
    def file_count_check(self,dir,exp_file_count,exp_file_list_str):
        #Defining module variables
        expected_file_count=int(exp_file_count)
        expected_file_list=exp_file_list_str.split(',')
        try:
            path, dirs, files = next(os.walk(dir))
            file_count = len(files)
            logging.info("------File Count Validation---------")
            logging.info("File count is %s",file_count)
            
            if file_count==expected_file_count:
                logging.info("Expected file count satisfied.")
                notify_email_msg="Expected file count satisfied."
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
            if file_count<expected_file_count:
                logging.error("Missing Files. Received  File count  %s. Exit program",file_count)
                self.file_list_check(dir,expected_file_list,type='missing_files')
                notify_email_msg="Missing Files. Refer log for Missing file names. \n Received File count="+str(file_count)
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                sys.exit(1)
            if file_count>expected_file_count:
                logging.error("Received more files than expected. Received file count: %s. Exit program",file_count)
                self.file_list_check(dir,expected_file_list,type='extra_files')
                notify_email_msg="Received Additional Files. Program Exit. Manually Run program. Received File count="+str(file_count)
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
 
        except OSError as e:
            logging.error(e)
            notify_email_msg='Error encountered during file count validation.'
            self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
    
    def file_list_check(self,dir,expected_list,type):
        file_exp=expected_list
        file_rcv=os.listdir(dir)  # Received files
        if type=='missing_files':
            #print("List of Files Expected : ",file_exp)
            #print("List of Files Received : ",file_rcv)
            logging.info("Number of missing files: {}".format(len((list(set(file_exp) - set(file_rcv))))))
            logging.info("List of missing files: {}".format((list(set(file_exp) - set(file_rcv)))))  # Print Missing files: Expected files that are not in Received files
        if type=='extra_files':
            logging.info("Number of Additional files: {}".format(len((list(set(file_rcv) - set(file_exp))))))
            logging.info("List of Additional files: {}".format((list(set(file_rcv) - set(file_exp))))) # Print additional files: More files received than expected
    

    def birst_upload(self,birst_cmd_dir,cmd_file,log_file_location,birst_space_name):
            logging.info("Upload Task Started for Space: %s",birst_space_name)
            logging.info("Upload Task Started for task: %s",cmd_file)
            space_name=birst_space_name.replace(" ","_")
            os.chdir(birst_cmd_dir)
            now = datetime.now()
            str_now=now.strftime("%Y-%m-%d_%H-%M-%S")
            birst_log=open(log_file_location+'birst_'+space_name+'_'+str_now+'.log', 'w')
            try:
                p = Popen(cmd_file,stdout=birst_log)    # open a batch file
                p.communicate()[0]                      # process.communicate starts polling the subprocess for a status 
                                                        # and keeps the connection to the subprocess open. 
                                                        # Thus, the interpreter has to wait until the subprocess execution 
                                                        # is complete in order to return program control back to main().
                rc = p.returncode
                if rc==0:
                    logging.info("Upload Task Completed sucessfully")
                    notify_email_msg="Upload Task Completed sucessfully"
                    self.notify_users(msgtype=notify_email_msg,attach='F',user_type='dev')
                if rc!=0:
                    raise Exception("Birst Connect Error occured and is exiting with non-zero status. Check birst log for additional information")
            except Exception as e:
                logging.error(e)
                notify_email_msg="Birst Connect Error occured and is exiting with non-zero status. Check birst log for additional information"
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                sys.exit(1)
    
    def process_data(self,url,birst_username, birst_password,birst_space,processingGroups,birst_space_name):
            logging.info('---------------Birst Processing Started---------------')
            #workflow: Login > publishData > isJobComplete > getJobStatus > Logout
            BirstUsername = birst_username
            BirstPassword = birst_password
            spaceId = birst_space
            wsdl = url
            try:
                client = zeep.Client(wsdl=wsdl)
                loginToken = client.service.Login(BirstUsername,BirstPassword)
                logging.info('Login Successful!. Token ID is %s',loginToken)
                ArrayOfString = client.get_type('ns0:ArrayOfString')
                logging.info('Processing Space: %s',birst_space_name)
                logging.info('Processing Groups passed as arguments to Birst_publishData function: %s', processingGroups)
                processingGroups_str=processingGroups
                processingGroups_list= processingGroups_str.split(',')
                processingGroups = ArrayOfString(processingGroups_list)
                publishToken=self.birst_publishData(client,loginToken,spaceId,processingGroups)
            except zeep.exceptions.Fault as f:
                logging.error('Error encountered')
                logging.error('Error Message: %s',f.message)
                logging.error('Error Code/ Category: %s',f.code)
                notify_email_msg='Error during Birst processing of space:'+birst_space_name
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                sys.exit(1)
            except zeep.exceptions.TransportError as te:
                logging.error("TransportError occured.")
                logging.error(te)
                notify_email_msg='Error during Birst processing of space:'+birst_space_name
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                sys.exit(1)
            except Exception as ex:
                logging.error('Error Encountered')
                logging.error(ex)
                notify_email_msg='Error during Birst processing of space:'+birst_space_name
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                sys.exit(1)
            logging.info('Publish Token is %s',publishToken)
            logging.info(client.service.isJobComplete(loginToken, publishToken)) #returns True / false
            
            try:
                jobstatus=self.birst_status_poll(client,loginToken, publishToken)
            
            except zeep.exceptions.TransportError as te:
                if te.status_code==504: 
                    logging.error(te)
                    time.sleep(15)
                    jobstatus=self.birst_status_poll(client,loginToken, publishToken)
                else:
                    logging.error(te)
                    time.sleep(15)
                    jobstatus=self.birst_status_poll(client,loginToken, publishToken)
            except Exception as ex:
                logging.error(ex)
                logging.error('Unidentified/Unhandled exception occured. System Exiting with Status Code 1')
                notify_email_msg='Unidentified/Unhandled exception occured. System Exiting with Status Code 1 during Birst processing of space:'+birst_space_name
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                return 1


            logging.info("Job Status Returned by getPublishingStatus function is %s",jobstatus) # Returns Complete/Failed/Running/None
            if jobstatus == 'Failed':
                print("Processing failed. Check Birst load log for details")
                logging.error("Status 'Failed' returned in job.getPublishingStatus")
                sys.exit(1)
                return 1
            if jobstatus == 'Complete': 
                print("Processing Successful! Check Birst load log for details")
                logging.info("getPublishingStatus method returned: %s",jobstatus)
                logging.info("Processing Successful! Check Birst load log for details")
                logging.info("Clearing Cache for space %s ",birst_space_name)
                client.service.clearCacheInSpace(loginToken,spaceId)
                logging.info("Completed Clearing Cache for space %s ",birst_space_name)
                return 0
            else:
                logging.error("Error Encountered in Birst publishing. Check Birst load log for details")
                notify_email_msg="Error Encountered in Birst publishing. Check Birst load log for details"
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                sys.exit(1)

            client.service.Logout(loginToken)
            
            msg = (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Processing completed. Check processing log for status!")
            logging.info(msg)
    
    def birst_publishData(self,client,loginToken,spaceId,processingGroups):
        try:
            max_poll_retries=int(self.max_poll_retries)
            publish_data_poll_timer=int(self.publish_data_poll_timer)
            logging.info("Space status is %s", client.service.getLoadStatus(loginToken,spaceId)) # Available, Processing
            for i in range(max_poll_retries):
                while True:
                    if client.service.getLoadStatus(loginToken,spaceId)=='Available':
                        publishToken = client.service.publishData(loginToken,spaceId,processingGroups,datetime.now())
                        return publishToken
                    else:
                        if i==max_poll_retries:
                            logging.info("Exceeded Max Retries for Birst Status polling. Exit System")
                            break
                        else:
                            logging.info("Waiting and Retrying space status polling...")
                            i=i+1
                            time.sleep(publish_data_poll_timer)
                break
            notify_email_msg='Exceeded Max Retries for Birst Status polling. Space in Unavailable state. Exit System.'
            self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
            sys.exit(1)
        except Exception as e:
            logging.error(e)

   
    def birst_status_poll(self,client,loginToken, publishToken):
            birst_status_poll_timer=int(self.birst_status_poll_timer)
            while True:
                # Successful Processing Status cycle: None -> Running -> Complete/Failed
                if client.service.isJobComplete(loginToken, publishToken):  #returns True / false
                        logging.info(client.service.isJobComplete(loginToken, publishToken)) #returns True / false
                        return str(client.service.getPublishingStatus(loginToken, publishToken)[0])
                        break
                logging.info("Processing...")
                logging.info("Publishing Status: %s",str(client.service.getPublishingStatus(loginToken, publishToken)[0]))
                time.sleep(birst_status_poll_timer) # status polling  every 1 minute


    def orchestrator1(self,root_dir):
        #00 Pipeline start notification
        notify_email_msg='Pipeline has started.'
        self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
        
        
        #1 File Count Validation:Check number of files in Process directory
        self.file_count_check(self.target_dir,self.expected_file_count,self.expected_file_list)
        
        
        #2 Birst Upload: Upload files in a directory via Birst Connect
        self.birst_upload(self.birst_cmd_dir,self.birst_connect_task,self.log_file_location,self.birst_space_name)

        
        #3 Birst Processing
        if self.process_data(self.birst_url,self.birst_username, self.birst_password,self.birst_space,
                            self.processingGroups,self.birst_space_name)==1:
                logging.info("Space Processing failed. Check Birst load log for details. Exit System.")
                notify_email_msg='Error'
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='user')
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
                sys.exit(1)
        else: 
            logging.info ("Processing of space %s completed Successfully",self.birst_space_name)
        

        #4 Log Completion and Notify Users
        logging.info('Job Completed at:%s',datetime.now())  # to do: fix time   
        end=datetime.now()
        pipeline_duration=end-self.start
        logging.info(f"Pipeline Duration: {pipeline_duration}")
        notify_email_msg='Success'
        self.notify_users(msgtype=notify_email_msg,attach='T',user_type='user')
        self.notify_users(msgtype=notify_email_msg,attach='T',user_type='dev')
        
 
        
            
if __name__ == "__main__":
    arg_list=str(sys.argv)
    root_dir=sys.argv[1]
    load_type=sys.argv[2]
      
    if load_type=="i": # arg 1 = root directory='E:\\automation', arg 2 ="i"  Command:python orchestrator.py E:\\automation i
        print("Run Incremental Load: orchestrator1")
        pipeline=automation_controller(root_dir)
        pipeline.orchestrator1(root_dir)
