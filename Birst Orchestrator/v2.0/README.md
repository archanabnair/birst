

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
   2. Birst Space details (URL, ServerURI, SpaceID, Processing groups, BirstConnect directory)
   3. Sender and Recipient information for Email Notifications

II. In the birst_upload_process.py script, in the __main__, pass the location which contains the config_auth.ini file

III. Set up Birst Connect.
   1. Log in to the Birst Space to which the files need to be uploaded to. 
   2. Download the JNLP file
   3. Download the BirstConnect.zip folder from Birst
   4. Extract the BirstConnect.zip contents into the root directory
   5. Replace the JNLP file inside the extracted folder with the JNLP file downloaded from the Birst space.
   6. In Notepad, open the cmdNoUI.bat file in 'commandline' folder and edit the file as shown in birstConnect.jpg file
   7. Rename the .bat file to all_tasks.bat

IV. Place the files to be uploaded in the directory referenced in the Birst Connect task. 

V.  To run the program:
   
   1. Copy birst_upload_process.py script into a local directory. 
   2. Open Command Line and navigate to the folder containing the .py file. 
   3. In the terminal, type "python birst_upload_process.py" and hit Enter. 
    
The program will create two logs in logs directory specified: one for the entire pipeline, and one specifically for Birst Connect Upload task. The log for the pipeline will also be attached in the Notification email send from the pipeline.

