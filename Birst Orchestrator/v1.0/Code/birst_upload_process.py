#*********************************************************************************************************************************
# Title: Pipeline orchestrator Script
# Author: Archana Balachandran
# Date: 2018-08-01
#
# Description: The script orchestrates the various activities in the data pipeline.
#              The various pipeline activities include:
#               1. Execute the Birst Connect JNLP tasks to upload the files to Birst
#               2. Process Data in Birst
#               3. Notify users upon pipeline completion
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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import COMMASPACE, formatdate



class automation_controller(object):
    def __init__(self,config_dir):
        self.config_dir=config_dir
        config_file_location=config_dir+'\\config_auth.ini'
        try:

            #0 Configure Log File and variables 
            now = datetime.now()
            config = configparser.ConfigParser()  #instantiate
            config.read(config_file_location) #parse config file
            self.root_dir=config.get('default','cwd')
            self.log_file_location=config.get('default','log_file')
            self.log_filename=self.log_file_init(self.log_file_location)
            logging.info('Job started at:%s',now)
            self.start=now   #Enhanced logging - for calculating pipeline duration
            
            # global
            self.cwd=config.get('default','cwd')

            # Notify 
            self.sender_email=config.get('notify','sender_email')
            self.sender_password=config.get('notify','sender_password')
            self.recipient_list=config.get('notify','recipient_email')
            self.dev_recipient_list=config.get('notify','recipient_email')
            self.smtp_host=config.get('notify','smtp_host')
            self.smtp_port=config.get('notify','smtp_port')
            # Birst Space

            self.url=config.get('connections.birst','url')
            self.birst_username=config.get('connections.birst','username')
            self.birst_password=config.get('connections.birst','password')
            self.birst_space=config.get('connections.birst','spaceID')
            self.birst_cmd_dir=config.get('connections.birst','cmd_dir')
            self.birst_connect_task=config.get('connections.birst','birst_connect_task')
            self.processingGroups=config.get('connections.birst','processingGroups')

            # Birst Batch Script
            self.JAVA_HOME=config.get('script.birst_batch_file','JAVA_HOME')
            self.BirstConnect_Home=config.get('script.birst_batch_file','BirstConnect_Home')
            self.JNLP_name=config.get('script.birst_batch_file','JNLP_name')
            self.JNLP_tasks=config.get('script.birst_batch_file','JNLP_tasks')


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
        
        if not os.path.exists(supplied_path):
            os.makedirs(supplied_path)
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
            filename=log_file_location+'\\'+self.log_filename
            attachment_name=self.log_filename
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
        server.sendmail(sender_email,email_send_list,text)

        server.quit()

   
    def birst_upload(self,dir,cmd_file):
            logging.info("Upload Task Started for task: %s",cmd_file)
            os.chdir(dir)
            now = datetime.now()
            str_now=now.strftime("%Y-%m-%d_%H-%M-%S")
            birst_log=open(self.log_file_location+str_now+'.log', 'w')
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
                msg='An error occurred during Birst Connect upload. Check Logs for details'
                self.notify_users(msg,attach='T',user_type='user')
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
            #publishToken = client.service.publishData(loginToken,spaceId,processingGroups,datetime.now())
            try:
                max_poll_retries=3
                publish_data_poll_timer=10
                max_poll_retries=int(max_poll_retries)
                publish_data_poll_timer=int(publish_data_poll_timer)
                logging.info("Space status is %s", client.service.getLoadStatus(loginToken,spaceId)) # Available, Processing
                for i in range(max_poll_retries):
                    while True:
                        if client.service.getLoadStatus(loginToken,spaceId)=='Available':
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
                                logging.info("Clearing Cache for space")
                                try:
                                    client.service.clearCacheInSpace(loginToken,spaceId)
                                except Exception as e:
                                    logging.info("Clear cache failed")
                                    logging.info(e)
                                logging.info("Completed Clearing Cache for space")
                            client.service.Logout(loginToken)
                            
                            
                            msg = (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Processing completed. Check processing log for status!")
                            logging.info(msg)
                            return 0
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
                self.notify_users(msgtype=notify_email_msg,attach='T',user_type='user')
                client.service.Logout(loginToken)
                sys.exit(1)
            except Exception as e:
                logging.error(e, exc_info=True)
            
    def birst_batch_file_creator(self):
        file = open("E://automation//testpipeline//testscript.bat","w") 
        file.write("set JAVA_HOME="+self.JAVA_HOME+'\n')
        file.write("set BirstConnect_Home="+self.BirstConnect_Home+'\n'+'\n')
        file.write('\"%JAVA_HOME%\\bin\java\" -cp \"%BirstConnect_Home%\\dist\*;%BirstConnect_Home%\\dist\lib\*\" -Djnlp.file=\"%BirstConnect_Home%\\'+self.JNLP_name+'\" -Xmx1024m com.birst.dataconductor.DataConductorCommandLine -tasks '+self.JNLP_tasks)
    
    def orchestrator(self,root_dir):
        logging.info("Pipeline Started")
        self.birst_batch_file_creator()
        
        #01. Run Birst Connect upload
        
        self.birst_upload(self.birst_cmd_dir,self.birst_connect_task)
                
        #02. Kick off Birst Processing
        
        if self.process_data(self.url,self.birst_username, self.birst_password,self.birst_space,self.processingGroups)==1:
                   msg='Space Processing failed. Check Birst load log for details'
                   logging.info(msg)
                   self.notify_users(msg,attach='T',user_type='user')
                   sys.exit(1)

        else:
            logging.info ("Automation Pipeline successfully executed. Check log for details.")
        
        #03. Log Completion and Notify Users
        logging.info('Job Completed at:%s',datetime.now())  # to do: fix time   
        end=datetime.now()
        pipeline_duration=end-self.start
        
        logging.info(f"Pipeline Duration: {pipeline_duration}")
        notify_email_msg='Success'
        self.notify_users(notify_email_msg,attach='T',user_type='user')
        
        
if __name__ == "__main__":
    arg_list=str(sys.argv)
    config_dir=sys.argv[1]
    pipeline_obj=automation_controller(config_dir)
    pipeline_obj.orchestrator(config_dir)
