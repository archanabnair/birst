#*********************************************************************************************************************************
# Title: Pipeline orchestrator Script
# Author: Archana Balachandran
# Date: 2018-08-01
#
# Description: The script orchestrates the various activities in the data pipeline.
#              The various pipeline activities include:
#               1. Transfer the encrypted files (50 files) from MFT into a dated S3 archive directory
#               2. Download the files from S3 archive to Local Staging
#               3. Perform file count validation. Exit on Failure.
#               4. Decrypt the files
#               5. Rename the files
#               6. Parse trailer record into load_control_file, strip trailer from file and transfer file to Birst pickup directory
#               7. Execute the Birst Connect JNLP tasks to upload the files to Birst
#               8. Process Data in Birst
#               9. Notify users upon pipeline completion
#                
#*********************************************************************************************************************************

import configparser     # Configuration file parser
import datetime         # Enables date functions
import io
import logging          # Log file management
import os               # system functions
import shutil           # File System functions (copy, remove file)
import smtplib          # Email for notifications
import sys              # Exit and stdout functions
import time             # Sleep function
import zeep             # Client interaction for Birst Web services
from datetime import datetime       # Date functions 
from subprocess import Popen,PIPE   # Enables access to system commands. Spawn processes, connect to I/O or error pipes, get return codes
from suds.client import Client      # SOAP-based web services client
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
        formatter=logging.Formatter('%(asctimme)s %(levelname)s: %(message)s')
        formatter.datefmt = '%m%d%Y %Y:%M:%S %p'
        scr.setFormatter(formatter)
        root_log.addHandler(scr)
        
        return file_name

    def notify_users(self,sender_email, sender_password,recipient_email,msgtype,log_filename,log_file_location):

        email_user = sender_email # get email from 'notifygmail' section in config file
        email_password =sender_password # get password from config file
        email_send=recipient_email # get recipient list
        #server = smtplib.SMTP('smtp.gmail.com', 587)


        subject = 'Pipeline Notification'

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = subject

        if msgtype=='Error':
            body = 'Hi \nThe pipeline has encountered an error and was terminated with status code 1. Refer log for details.\n\nBirst Automation Team'
        if msgtype=='Success': 
            body = 'Hi \nThe pipeline was executed successfully. Check attached log for details. \n\nBirst Automation Team'
        msg.attach(MIMEText(body,'plain'))

        filename=log_file_location+'\\'+log_filename
        attachment_name=log_filename
        attachment  =open(filename,'rb')

        part = MIMEBase('application','octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',"attachment; filename= "+attachment_name)

        msg.attach(part)
        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls() # Required for port 587 on SMTP server. Enables encryption and  upgrades an existing insecure connection to a secure connection using SSL/TLS
        server.login(email_user,email_password)


        server.sendmail(email_user,email_send,text)
        server.quit()

   
    def birst_upload(self,dir,cmd_file):
            logging.info("Upload Task Started for task: %s",cmd_file)
            os.chdir(dir)
            now = datetime.now()
            str_now=now.strftime("%Y-%m-%d_%H-%M-%S")
            birst_log=open(r'E:\automation\logs\birst'+str_now+'.log', 'w')
            try:
                p = Popen(cmd_file,stdout=birst_log)    # open a batch file
                p.communicate()[0]                      # process.communicate starts polling the subprocess for a status 
                                                        # and keeps the connection to the subprocess open. 
                                                        # Thus, the interpreter has to wait until the subprocess execution 
                                                        # is complete in order to return program control back to main().
                rc = p.returncode
                if rc==0:
                    logging.info("Upload Task Completed sucessfully")
                if rc==1:
                    raise Exception("Birst Connect Error occured and is exiting with non-zero status. Check birst log for additional information")
            except Exception as e:
                logging.error(e)
                sys.exit()

    def process_data(self,url,birst_username, birst_password,birst_space,processingGroups):
            logging.info('---------------Birst Processing Started---------------')
            #workflow: Login > publishData > isJobComplete > getJobStatus > Logout
            BirstUsername = birst_username
            BirstPassword = birst_password
            spaceId = birst_space
            wsdl = url
            client = zeep.Client(wsdl=wsdl)
            loginToken = client.service.Login(BirstUsername,BirstPassword)
            logging.info('Login Successful!. Token ID is %s',loginToken)
            ArrayOfString = client.get_type('ns0:ArrayOfString')
            logging.info('Processing Groups passed as arguments to Birst_Upload function: %s', processingGroups)
            processingGroups_str=processingGroups
            processingGroups_list= processingGroups_str.split(',')
            processingGroups = ArrayOfString(processingGroups_list)
            publishToken = client.service.publishData(loginToken,spaceId,processingGroups,datetime.now())
            logging.info('Publish Token is %s',publishToken)
            print(client.service.isJobComplete(loginToken, publishToken))
            while True:
                # Successful Processing Status cycle: None -> Running -> Complete
                if client.service.isJobComplete(loginToken, publishToken):
                        print(client.service.isJobComplete(loginToken, publishToken))
                        break
                logging.info("Processing...")
                logging.info("Publishing Status: %s",str(client.service.getPublishingStatus(loginToken, publishToken)[0]))
                logging.info("Publishing Status: %s",str(client.service.getPublishingStatus(loginToken, publishToken)))

                time.sleep(180) # status polling  every 3 minutes
            logging.info(str(client.service.getPublishingStatus(loginToken, publishToken)[0]))
            if str(client.service.getPublishingStatus(loginToken, publishToken)[0]) == 'Failed':
                print("Processing failed. Check Birst load log for details")
                logging.info("Status 'Failed' returned in job.getPublishingStatus")
                return 1
            else: 
                print("Processing Successful! Check Birst load log for details")
                logging.info("Processing Successful! Check Birst load log for details")
            client.service.Logout(loginToken)
            
            msg = (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Processing completed. Check processing log for status!")
            logging.info(msg)
           
        
    def orchestrator(self,root_dir):
        try:

            #0 Configure Log File and variables 
            os.chdir(root_dir)
            now = datetime.now()
            config = configparser.ConfigParser()  #instantiate
            config.read('config_auth.ini') #parse config file
            log_file_location=config.get('default','log_file')
            log_filename=self.log_file_init(log_file_location)
            logging.info('Job started at:%s',now)
            start=now   #Enhanced logging - for calculating pipeline duration
            
            # global
            cwd=config.get('default','cwd')

            # Notify
            sender_email=config.get('notify','sender_email')
            sender_password=config.get('notify','sender_password')
            recipient_list=config.get('notify','recipient_email')
                        
            # Birst Space

            url=config.get('connections.birst','url')
            birst_username=config.get('connections.birst','username')
            birst_password=config.get('connections.birst','password')
            birst_space=config.get('connections.birst','spaceID')
            birst_cmd_dir=config.get('connections.birst','cmd_dir')
            processingGroups=config.get('connections.birst','processingGroups')

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

        
        #01. Run Birst Connect upload
        self.birst_upload(birst_cmd_dir,"all_tasks.bat")
                
        #02. Kick off Birst Processing
        
        if self.process_data(url,birst_username, birst_password,birst_space,processingGroups)==1:
                   logging.info("Space Processing failed. Check Birst load log for details")
        else:
            logging.info ("Automation Pipeline successfully executed. Check log for details.")
                   
        #03. Log Completion and Notify Users
        logging.info('Job Completed at:%s',datetime.now())  # to do: fix time   
        end=datetime.now()
        pipeline_duration=end-start
        
        logging.info(f"Pipeline Duration: {pipeline_duration}")
        notify_email_msg='Success'
        self.notify_users(sender_email,sender_password,recipient_list,notify_email_msg,log_filename,log_file_location)
  
if __name__ == "__main__":
    automation_controller().orchestrator('E:\\automation')

