
## Birst Orchestrator 

### Pre-requisities
|Requirement|Description|
|:---                   |:---       |
|Python| Requires python 3.4+|
|Code Editor|Notepad++/VS Code/PyCharm|
|Python packages|List provided in the documentation|
|Birst|Birst Connect, Birst Space ID, Birst user credentials|


### Usage

The birst_upload_process.py script achieves the following functionality:
1. Upload files from a local directory to Birst
2. Triggers Birst Processing upon completion of file upload
3. Notifies users upon completion of pipeline, with the execution log as attachment

The following modifications need to be made in order to re-use the code: 

I. Place the config_auth.ini file in root directory. Open config_auth.ini and specify:
   1. Current Working Directory, Log file location
   2. Birst Space details (URL, SpaceID, Processing groups, BirstConnect directory)
   3. Sender and Recipient information for Email Notifications
   4. Birst Connect Batch File contents - verify/update parameters as required (jnlp name, task list, java home, birst connect home)

II . Set up Birst Connect.
   1. Log in to the Birst Space to which the files need to be uploaded to. 
   2. Download the JNLP file and place in root_dir/BirstConnect folder

III. Place the files to be uploaded in the directory referenced in the Birst Connect task. 

IV.  To run the program:
   
   1. Place birst_upload_process.py script into root_dir. Place config file in root_dir. 
   2. Open Command Line and navigate to root_dir using 'cd' command. 
   3. In the terminal, type "python birst_upload_process.py <" and hit Enter. 
    
The program will create two logs in logs directory specified: one for the entire pipeline, and one specifically for Birst Connect Upload task. The log for the pipeline will also be attached in the Notification email send from the pipeline.

