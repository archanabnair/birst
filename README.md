# Birst Upload and Processing

The birst_upload_process.py script achieves the following functionality:
1. Upload files from a local directory to Birst
2. Triggers Birst Processing upon completion of file upload

The following modifications need to be made in order to re-use the code: 
Open config_auth.ini and specify:
1. Current Working Directory, Log file location
2. Birst Space details (URL, ServerURI, SpaceID, Processing groups)
3. Sender and Recipient information for Email Notifications
 In the birst_upload_process.py script, in the __main__, pass the location which contains the config_auth.ini file


For any questions or enhancement requests, contact abalachandran@mycervello.com.
