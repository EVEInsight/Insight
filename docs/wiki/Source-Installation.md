# Installation Options
This installation guide covers installing Insight and the required packages from source. Binary versions and a Docker image of Insight are available. See [hosting Insight](https://github.com/Nathan-LS/Insight#hosting-insight) for alternative methods of hosting Insight. Please consider using the Docker image of Insight if you are unfamiliar with installing packages or running applications on the Python Interpreter in Linux. Please be aware that running Insight from source specifically requires a Python 3.6 interpreter.

# Table of Contents
- [Installation Options](#installation-options)
- [Table of Contents](#table-of-contents)
- [Requirements (installing from source)](#requirements--installing-from-source-)
- [Installation steps](#installation-steps)
    - [Cloning the project and making your virtualenv](#cloning-the-project-and-making-your-virtualenv)
    - [Installing Required Packages](#installing-required-packages)
    - [SDE database and cleaning files](#sde-database-and-cleaning-files)
    - [Configuration Steps](#configuration-steps)
      - [Discord](#discord)
      - [EVE Developer](#eve-developer)
- [Running Insight](#running-insight)
    - [Inviting your new bot](#inviting-your-new-bot)
- [Further Reading](#further-reading)

# Requirements (running from source)
* Python 3.6 (Prior versions of Python will not work. Python 3.7+ is currently unsupported.)
* Packages in requirements.txt
* The latest [sqlite-latest.sqlite.bz2](https://www.fuzzwork.co.uk/dump/) from Fuzzwork
* Git

# Installation steps
This guide will step you through setting up Insight on a Debian/Ubuntu operating system. 

Note: A recent version of Ubuntu 18.04+ is recommended as Python 3.6 is included in the default repositories. You will need to build Python 3.6 from source if your Linux distribution only includes an earlier version of python in the repositories. It is generally not recommended to mix multiple Python 3 versions on a system as things can break. 

Let's start by making sure we have all of the required packages needed to run Insight:
```
sudo apt-get update
sudo apt-get install git python3 python3-dev python3-pip python3-venv wget unzip
```
When you run the command 
```
python3 -V
```
You should see:
```
Python 3.6.x
```
Note: Insight requires Python 3.6 specifically. Earlier versions lack support for some of the asyncio features and syntax used in Insight. Python 3.7 causes issues with the third-party swagger-client which will eventually be replaced.

### Cloning the project and making your virtualenv
Navigate to where you wish to keep the Insight project and make a new project directory. In this example we will create a directory in the current user's home directory to store files.
```
mkdir ~/InsightProjectFiles
cd ~/InsightProjectFiles
```
Clone the project from Github:
```
git clone https://github.com/Nathan-LS/Insight.git
```
Let's create a python virtual environment in the Insight project directory and activate it. A virtual environment allows the user to install python packages to a virtual environment on a per-project basis without installing them to the global Python environment. 
```
cd Insight
python3 -m venv venv
source venv/bin/activate
```

### Installing required packages
We are now ready to start installing required packages to our activated virtual environment. First, we need to install the Swagger python-client. This is an automatically generated library using the Swagger code generator for the EVE Online API. This library is now generated and provided under Insight releases. If you wish to generate the library yourself, see [CCP Codegen Blog](https://developers.eveonline.com/blog/article/swagger-codegen-update). The following steps assume you are downloading the swagger-client from Insight releases.


Download the latest swagger-client release. Replace the version number with the latest Insight release version.
```
wget https://github.com/Nathan-LS/Insight/releases/download/v1.4.0/swagger-client-python.zip
unzip swagger-client-python.zip -d swagger-client-python
cd swagger-client-python
```

Now we will install the python-client to the venv.
```
python3 setup.py install
cd ..
```

Now we will install the remaining packages specified in Insight's requirements.txt file with the following command.
```
pip3 install -r requirements.txt
```

### SDE database
Download and extract the latest SDE sqlite database archive from Fuzzwork.
```
wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
bunzip2 sqlite-latest.sqlite.bz2
```

### Configuration Steps
We now need to create Discord and CCP Developer applications.

Open the file **default-config.ini** in a text editor or run this command if using the command line interface:
```
nano default-config.ini
```

#### Discord
Navigate to [Discord Applications](https://discordapp.com/developers/applications/me) in a web browser, click **My Apps** and then **New App**.

Name your app and provide a description. No redirect URL is required. After clicking **Create App**, select **Create a Bot User**.

Check **Public Bot** and uncheck **Require OAuth2 Code Grant**

Click **click to reveal** next to **Token** under the Bot settings. Copy this token down and paste it into the correct section in your config file as seen below:

```
[discord]
token = YourDiscordAppTokenGoesHere
;required - Create a new Discord app at https://discordapp.com/developers/applications/me and set token to your App's token

```

#### EVE Developer
Insight requires an EVE Application to access user contacts for use in cap radar feeds. Navigate to [Create New App](https://developers.eveonline.com/applications/create).

Provide a name and description for your app and select **Authentication & API Access** for **Connection Type**

In the **Permissions** pane make sure the following scopes are listed under **Requested Scopes List**:
* esi-characters.read_contacts.v1
* esi-corporations.read_contacts.v1
* esi-alliances.read_contacts.v1

Specify ```https://localhost/InsightCallback``` as your **Callback URL**. After authenticating, Discord users will be redirected to your callback URL. You can modify the URL to point to your website if you host a custom landing page, otherwise the user will simply be directed to a blank page on localhost after which they paste the given callback URL into the Discord direct message. 

Click **Create Application** and then view your newly created application. Copy the **Client ID:**, **Secret Key**, and **Callback URL:** into the appropriate sections in your open configuration file like so:
```
[ccp_developer]
client_id = ExampleClientIDGoesHere
secret_key = ExampleSecretKeyGoesHere
callback_url = ExampleCallbackURLGoesHere
;required - Create a new CCP Application at https://developers.eveonline.com/applications/create with the following scopes:
;esi-characters.read_contacts.v1
;esi-corporations.read_contacts.v1
;esi-alliances.read_contacts.v1
```

Save and rename your configuration file to **config.ini**, moving it to the current directory. If you are using nano and the CLI, use the following shortcuts: **'CRTL-X'**, **'Y'**, **'ENTER'** and run the command:

```
mv default-config.ini config.ini
```


# Running Insight
Congratulations! You are now ready to run Insight! To start Insight using your virtual environment run:

```
python3 Insight
```
Insight will start and begin importing data from the SDE. On the first initial run it can take up to 10 minutes to import everything from the SDE. On subsequent runs Insight will only import missing static data which takes little time.

### Inviting your new bot
You need your Discord application's client ID found [here](https://discordapp.com/developers/applications/me) to invite your newly created bot. Select your Discord application and copy down the **Client ID**.

Edit the following URL to include your **Client ID**. Navigating to this URL will allow users to invite the bot to their server.
```
https://discordapp.com/api/oauth2/authorize?client_id=ClientIDGoesHere&permissions=0&scope=bot
``` 

# Further Reading
* [Running Insight in the background with Ubuntu](https://github.com/Nathan-LS/Insight/wiki/Running-Insight-in-the-background-(source-only)#running-insight-in-the-backgroundubuntu)
* [Start Insight at Ubuntu boot](https://github.com/Nathan-LS/Insight/wiki/Running-Insight-in-the-background-(source-only)#start-insight-on-startup-ubuntu)
