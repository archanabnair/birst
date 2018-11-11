
## Birst Orchestrator 

The birst_upload_process.py script achieves the following functionality:
1. Upload files from a local directory to Birst
2. Triggers Birst Processing upon completion of file upload
3. Notifies users upon completion of pipeline, with the execution log as attachment

### Pre-requisities

|Requirement|Description|
|:---                   |:---       |
|OS|Windows / Linux|
|Python| Requires python 3.4+|
|Text Editor to modify Configuration file|Notepad++/Notepad/Wordpad|
|Birst|Birst Connect JNLP|

### Set up


1. Check Python Version: Open Command window and type: 
   >**python --version**
   
   If version < 3.6, download the preferred version from https://www.python.org/downloads/release/python-370/
   
2. Check if Pip version is up-to-date: Open Command window and type:
   >**python -m pip install --upgrade pip**
   
3. Place the **setup.py** script in the folder dedicated for Automation. For example, C:/birstautomation/setup.py

4. Run the script by double clicking **setup.py**. This installs all required Python modules and required directories. You can check the log for setup in logs directory, with the filename **setup_timestamp.log**

5. Place the **birst_upload_process.py** script and **config_auth.ini** file in the folder **C:/birstautomation/**

6. Open config_auth.ini and modify details as per your requirement. Detailed explanation on each parameter is below. 

7. Set up Birst Connect:
+ Log in to the Birst Space to which the files need to be uploaded to. 
+ Download the JNLP file and place in **C:/birstautomation/BirstConnect** folder
+ Place the files to be uploaded to Birst in the directory referenced in Birst Connect tasks. 

Once setup is complete, the contents of your directory will look like this:


|File/Directory|
|:---                   |
|<root_dir>/birst_upload_process.py||
|<root_dir>/config_auth.ini||
|<root_dir>/setup.py||
|<root_dir>/BirstConnect/<space_id.jnlp>||
|<root_dir>/Logs||



### Usage

To run the program:
   
   1. Open Command Line and navigate to root_dir using 'cd' command. 
   2. In the terminal, type the following and hit Enter:
  >**python birst_upload_process.py C:/birstautomation/config_auth.ini**
 
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


### Required Python Packages (installed by Setup.py)

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
+ subprocess 
+ email
