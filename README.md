# log_uploader
A log uploader app that is smart about taking too much space in the filesystem and monitoring the upload timeouts.

Given a robot with various sensory inputs and existing functionality of localization and control, implement a data manager class.

Details:

What already exists:
- Robot has sensor drivers emitting sensor data at various frequencies and payload sizes
- Robot has a data recorder, which is similar to a flight recorder box on an aircraft. It is a process (in ROS terms it would be a ROS bagging node) writing all sensor data and other relevant information periodically to disk:
    - Based on a config.json file (expressing things like the frequency of writes to disk plus the location of these data files), a concrete example would be that the data recorder saves every 10 minutes a new zip file comprised of all the interesting data (sensors, etc.) to /home/data
    - For instance after 30 minutes of operating the robot's /home/data folder looks like this:

```
ls -al /home/data
drwxr-xr-x   3 volley  300MB Aug 10 09:00 file1.zip
drwxr-xr-x   3 volley  310MB Aug 10 09:10 file2.zip
drwxr-xr-x   3 volley  305MB Aug 10 09:20 file3.zip
```

So, the Robot is happily driving around. Sometimes we experience bugs and need to debug why the robot took certain actions.

We need a data manager, which has two main responsibilities:
1) Upload that data produced by the data-recorder to the cloud. (you can assume there is an existing library function "def cloud_upload(str file_path)" to upload a file to some cloud storage system. from there engineers can download that file and debug interesting cases. This function is blocking)

2) Prevent the robot from running out of disk space. Our robot has only 10GB of disk space and if this gets full, Linux will evict randomly processes, which can be the controller process or other important units leading to unexpected robot behavior.

You can also assume you have any filesystem functions at your disposal, like "delete_file", "directory_size", "file_size", "list_files", etc.

## Running
Tested with Python 3.10. 
```
python -m venv .venv; source .venv/bin/activate # setup a virtual environment
pip install -r requirements.txt
python src/log_uploader.py
```

## Testing
```
PYTHONPATH=src
pytest test/test.py
```