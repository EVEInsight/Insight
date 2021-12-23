# Supported tags and ```Dockerfile``` links
* [```1.5.1```, ```1.5```, ```latest```](https://github.com/Nathan-LS/Insight/blob/master/scripts/Docker/Dockerfile)
* [```1.7.0-dev```, ```1.7-dev```, ```development```](https://github.com/Nathan-LS/Insight/blob/development/scripts/Docker/Dockerfile)
* [```1.6.0-dev```, ```1.6-dev```](https://github.com/Nathan-LS/Insight/blob/ad6c10970738a65d4fbc80cdbb1beb0fb4c150e1/scripts/Docker/Dockerfile)

# Quick reference
* **Where to get help:**

    [Insight Discord support server](https://discord.gg/Np3FCUn)
* **Where to file issues:**
    
    [https://github.com/Nathan-LS/Insight/issues](https://github.com/Nathan-LS/Insight/issues)

# What is Insight?
Insight provides EVE Online killmail streaming for Discord. Insight can stream personal or corporate killboards, detect supercapitals with a proximity radar, and more!
Killmails and intel are presented in Discord rich embeds containing relevant links and images to quickly identify important information.

# Feature Overview
* Entity feeds ideal for personal, corporate, or alliance killboard streaming.
* Radar feeds ideal for tracking hostile incursions into friendly space, hunting expensive targets within jump range, or detecting capital escalations in real time.
* Proximity watches ideal for finding potential fleets to fight, tracking hostile fleet movement within your region, or alerting you of nearby hostiles within a few jumps of your base systems.
* Preconfigured feeds offering custom spins such as: Alliance Tournament system feed, npc officer hunter, AT ship radar, and more!
* Rich embeds to present mails with color indicating sidebars, hyperlinks, and images.
* Multiple embed appearance styles varying in size and verbosity.
* Optional mention system to be alerted of activity in radar feeds.
* SSO token authentication for allied contact blacklisting in radar feeds.
* Automatic synchronization of SSO tokens and radar blacklists.
* Instinctual commands and convenient option dialogs for managing settings.
* Easy server setup with no hardcoding or confusing configuration.
* Simultaneous, isolated feeds across multiple servers.
* Efficient asynchronous design with minimal cpu, memory, disk, and network impact.  

# Start an ```Insight``` instance
This Docker image uses volumes to persist the Database.db and config file. See [volumes](https://docs.docker.com/storage/volumes/) for information about Docker volumes.
1. Create and navigate to a directory where you wish to store Insight configuration, logs, and database.
2. Pull and run the image. This command will pull the stable Docker Insight image and initialize the config files in your current directory.
    ```
    docker run --name insight -it --rm -v ${PWD}:/app nathanls/insight --docker-init
    ```
3. Edit ```default-config.ini``` and populate your configuration values in accordance with the [Configuring Insight](#configuring-insight) section. Rename this file to ```config.ini```.
4. Keep the image up to date by checking for updates and then starting Insight: 
    ```
    docker pull nathanls/insight && docker run --name insight -it --rm -v ${PWD}:/app nathanls/insight
    ```

# via ```docker stack deploy``` or ```docker-compose```
Example ```stack.yml``` for ```insight```:
```text
version: '3.1'
services:
  insight:
    image: nathanls/insight:stable
    restart: always
    volumes:
      - ./:/app
    stdin_open: true
    tty: true
```

# Configuring Insight
1. Find and open the 'default-config.ini' file with a text editor.
2. Go to [Discord Developer](https://discordapp.com/developers/applications/me) and create a **New App**.
    * No **Redirect URL** is required.
    * After creating a new app, edit your app and click **Create a Bot User**.
    * Ensure the **Public Bot** checkbox is enabled and the **Require OAuth2 Code Grant** is disabled.
3. Copy your Discord application's **Token** into the config file under the section [discord]. Your config file section should look
like this:
    ```
    [discord]
    token = YourDiscordAppTokenGoesHereWithoutQuotes
    ;required - Create a new Discord app at https://discordapp.com/developers/applications/me and set token to your App's token
    ```
4. Go to [CCP Developers](https://developers.eveonline.com/applications/create) and create a new app with the following settings:
    * **Connection Type** = Authentication & API Access
    * **Requested Scopes List:**
        * esi-characters.read_contacts.v1
        * esi-corporations.read_contacts.v1
        * esi-alliances.read_contacts.v1
    * **Callback** = ```https://github.eveinsight.net/Insight/callback``` if you don't plan on personally hosting a callback landing page.
        * Insight does not utilize a callback listener for simplicity so the user must manually copy their returned callback URL into Discord.
    Feel free to host the contents of /callback/index.html and modify the callback to point to your own landing page. The above URL is hosted on Github and directs users to the contents of ```Insight/callback/index.html```.
5. Create your new CCP App and copy the **Client ID**, **Secret Key**, and **Callback URL** into the appropriate sections in your **config** file.
6. Save your config file and rename it from ```default-config.ini``` to ```config.ini```.

# Updating
This Docker repository utilizes automated builds. The Docker images are automatically updated whenever there are new commits to the [Git repo](https://github.com/Nathan-LS/Insight). You can update your image locally by running a pull command and restarting the Docker container:
```
docker pull nathanls/insight
```
There is no need to manually update the SDE or any files associated with the Insight build as the latest dependencies are all included within the image.

# Inviting your bot
1. Find your Discord application's id from [Discord Apps](https://discordapp.com/developers/applications/me).
2. Edit this URL to include your app's client ID:
    ```
    https://discordapp.com/api/oauth2/authorize?client_id=YourClientIDHere&permissions=149504&scope=bot
    ```
**or**
* A link is provided when Insight starts. Check the program console and copy down the **Invite Link**.