
## Birst Orchestrator 

The birst_upload_process.py script achieves the following functionality:
1. Upload files from a local directory to Birst
2. Triggers Birst Processing upon completion of file upload
3. Notifies users upon completion of pipeline, with the execution log as attachment

### Pre-requisities

|Requirement|Description|
|:---                   |:---       |
|Python| Requires python 3.4+|
|Code Editor|Notepad++/VS Code/PyCharm|
|Python packages|List provided in the documentation|
|Birst|Birst Connect, Birst Space ID, Birst user credentials|

### Set up

|File/Directory|Set-up|
|:---                   |:---       |
|<root_dir>/birst_upload_process.py|Place python script in <root_dir>|
|<root_dir>/config_auth.ini|Place configuration file in <root_dir>|
|<root_dir>/BirstConnect|Manually create this directory in root_dir. Specify location in Config file.|
|<root_dir>/Logs|Automatically created by program|
|<root_dir>/BirstConnect/tasks.bat file|Automatically created by program. Verify information in Config file.|


The following modifications need to be made in order to re-use the code: 

I. Place the Python script in root directory.
II. Place the config_auth.ini file in root directory. Open config_auth.ini and specify:
   1. Current Working Directory, Log file location
   2. Birst Space details (URL, SpaceID, Processing groups, BirstConnect directory)
   3. Sender and Recipient information for Email Notifications
   4. Birst Connect Batch File contents - verify/update parameters as required (jnlp name, task list, java home, birst connect home)

III. Set up Birst Connect.
   1. Log in to the Birst Space to which the files need to be uploaded to. 
   2. Download the JNLP file and place in root_dir/BirstConnect folder

IV. Place the files to be uploaded in the directory referenced in the Birst Connect task. 

### Usage

To run the program:
   
   1. Open Command Line and navigate to root_dir using 'cd' command. 
   2. In the terminal, type the following and hit Enter:
  >**python birst_upload_process.py /path/to/config/file/config_auth.ini**
 
The program will create two logs in logs directory specified: one for the entire pipeline, and one specifically for Birst Connect Upload task. The log for the pipeline will also be attached in the Notification email sent from the pipeline.

### Config File Contents

|Section|Option|Description|
|:---                   |:---       |:---       |
|default|cwd|Specify Current Working Directory (or root_dir containing the Python script, config file, BirstConnect folder)|
|default|log_file|Specify the desired location for maintaining Log files|
|notify|sender_email|Specify the email address of person sending the email notifications from pipeline|
|notify|sender_password|Specify the email password of person sending the email notifications from pipeline|
|notify|recipient_email|Specify the email address of recipient(s) of the email notifications from pipeline. Comma-separated list.|
|notify|smtp_host|Specify SMTP host server details|
|notify|smtp_port|Specify SMTP port details|
|connections.birst|url|Birst URL. Ensure to append '/CommandWebService.asmx?wsdl' as suffix|
|connections.birst|username|Specify Birst username for user who will be executing the Processing in Birst|
|connections.birst|password|Specify Birst password for user who will be executing the Processing in Birst|
|connections.birst|spacename|Specify space name (You can find this in Modify Properties in Birst)|
|connections.birst|spaceID|Specify space ID (You can find this in Modify Properties in Birst)|
|connections.birst|processingGroups|Specify Processing groups to be run in Birst. If multiple processing groups need to be processed, specify as a comma separated string. They will be processed in alphabetical/numerical order.|
|connections.birst_connect|BirstConnect_Home|Specify directory containing the JNLP file downloaded from the Birst space|
|connections.birst_connect|birst_connect_batch_filename|Specify the desired name to be given to the Batch file containing the Birst Connect tasks|
|connections.birst_connect|JAVA_HOME|Specify the JAVA location on the system|
|connections.birst_connect|JNLP_name|Specify name of the JNLP file downloaded from the Birst space|
|connections.birst_connect|JNLP_tasks|Specify the Birst Connect tasks to be run|


### Required Python Packages

+ configparser    
+ datetime         
+ io
+ logging           
+ os                
+ shutil            
+ smtplib          
+ sys               
+ time              
+ zeep             
+ datetime 
+ subprocess 
+ email
