# Running Insight in the background(Ubuntu)
Insight includes startup and stop shell scripts in the **/scripts** directory.
Ensure you have **screen**:
```
sudo apt-get update
sudo apt-get install screen
```
Allow the files to have execute permissions:
```
cd scripts
chmod +x insight_start.sh
chmod +x insight_stop.sh
```

Execute the script, assuming you have a python virtual environment named **venv** in the Git root directory.
```
./insight_start.sh
```
Will start insight in a screen session accessible by running:
```
screen -r eveInsight
```

You can use the keyboard shortcut **CRTL-A-D** to minimize the screen session into the background. To terminate Insight, run:
```
screen -S eveInsight -X quit
```
or execute the provided ```insight_stop.sh``` script.


# Start Insight on startup (Ubuntu)
You can edit crontab to start Insight on startup using the provided shell scripts.
```
crontab -e
```

Add the following entry at the end of the file:
```
@reboot ~/YourPathToInsightGitFolder/scripts/insight_start.sh
```

Save this file with the shortcuts: **'CRTL-X'**, **'Y'**, **'ENTER'** if you are using **nano**. Now when Ubuntu starts the Insight startup script will be called, creating a screen session named **eveInsight**.
 


