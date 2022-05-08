# Project Status
This project and Docker repository is no longer actively maintained or supported. See [The Future of Insight](https://github.com/EVEInsight/Insight/blob/master/the_future_of_Insight.md) document for reasoning and an FAQ.
Thank you all for supporting and enjoying Insight over the years!

Fly safe o7


[![](https://img.shields.io/badge/-EVEInsight.net-154360)](https://eveinsight.net)

[Insight](https://git.eveinsight.net) Discord bot for EVE Online.

# Supported tags and ```Dockerfile``` links
* [```1.7.0```, ```1.7```, ```latest```](https://github.com/EVEInsight/Insight/blob/master/scripts/Docker/Dockerfile)
* [```1.7.0-dev```, ```1.7-dev```, ```development```](https://github.com/EVEInsight/Insight/blob/development/scripts/Docker/Dockerfile)
* [```1.6.0-dev```, ```1.6-dev```](https://github.com/EVEInsight/Insight/blob/ad6c10970738a65d4fbc80cdbb1beb0fb4c150e1/scripts/Docker/Dockerfile)

# Quick reference
* **Where to get help:**

    [Insight Discord support server](https://discord.gg/Np3FCUn)
* **Where to file issues:**
    
    [https://github.com/EVEInsight/Insight/issues](https://github.com/EVEInsight/Insight/issues)

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
1. Pull and run the image. This command will pull the latest Insight Docker image. Note: this command does not persist any Docker volume data.
    ```
    docker run --name insight -it --rm nathanls/insight
    ```
2. Keep the image up to date by checking for updates and then starting Insight: 
    ```
    docker pull nathanls/insight && docker run --name insight -it --rm nathanls/insight
    ```

# via ```docker stack deploy``` or ```docker-compose```
Example ```stack.yml``` for ```insight```:
```yaml
version: '3.1'
services:
  insight:
    image: nathanls/insight:latest
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: any
    environment:
      DB_DRIVER: "sqlite3"
      SQLITE_DB_PATH: "Database.db"
      HEADERS_FROM_EMAIL: "YourEmailHere"
      DISCORD_TOKEN: "DiscordBotTokenHere"
      CCP_CLIENT_ID: "YourDevAppInfoHere"
      CCP_SECRET_KEY: "YourDevAppInfoHere"
      CCP_CALLBACK_URL: "https://github.eveinsight.net/Insight/callback/index.html"
      REDIS_HOST: "redis"
      REDIS_PORT: 6379
      REDIS_PASSWORD: "pass"
      REDIS_PURGE: "FALSE"
      REDIS_SSL: "FALSE"
      INSIGHT_ADMINS: "YourDiscordPublicUserID; AnotherAdminUserID"
      WEBSERVER_ENABLED: "FALSE"
    volumes:
      - insight-data:/app
    networks:
      - insight-net
  redis:
    image: redis:6
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: any
    networks:
      - insight-net
    command: --requirepass "pass"
networks:
  insight-net:
    driver: overlay
volumes:
  insight-data:
```

# Configuring Insight
1. Go to [Discord Developer](https://discordapp.com/developers/applications/me) and create a **New App**.
    * No **Redirect URL** is required.
    * After creating a new app, edit your app and click **Create a Bot User**.
    * Ensure the **Public Bot** checkbox is enabled and the **Require OAuth2 Code Grant** is disabled.
2. Copy your Discord application's **Token** and set the ```DISCORD_TOKEN``` environmental variable.
3. Go to [EVE App Developers](https://developers.eveonline.com/applications/create) and create a new app with the following settings:
    * **Connection Type** = Authentication & API Access
    * **Requested Scopes List:**
        * esi-characters.read_contacts.v1
        * esi-corporations.read_contacts.v1
        * esi-alliances.read_contacts.v1
    * **Callback** = ```https://github.eveinsight.net/Insight/callback``` if you don't plan on personally hosting a callback landing page.
        * Insight does not utilize a callback listener for simplicity in the default config so the user must manually copy their returned callback URL into Discord.
    Feel free to host the contents of /callback/index.html and modify the callback to point to your own landing page. The above URL is hosted on Github and directs users to the contents of ```Insight/callback/index.html```.
4. Create your new CCP App and copy the **Client ID**, **Secret Key**, and **Callback URL** and set the ```CCP_CLIENT_ID```, ```CCP_SECRET_KEY```, and ```CCP_CALLBACK_URL``` environmental variables.

# Updating
This Docker repository utilizes automated builds. The Docker images are automatically updated whenever there are new commits to the [Git repo](https://github.com/EVEInsight/Insight). You can update your image locally by running a pull command and restarting the Docker container:
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


# Environment Variables
The follow section details available environmental variables that can be passed to modify Insight behavior.

Not all variables are listed here as they cover niche use cases. 
See [Dockerfile](https://github.com/EVEInsight/Insight/blob/master/scripts/Docker/Dockerfile) and [ConfigLoader.py](https://github.com/EVEInsight/Insight/blob/master/Insight/InsightUtilities/ConfigLoader.py) for an idea of all available env variables.

### ```DB_DRIVER```
The database driver to use. Can be ```sqlite3``` or ```postgres```. 
If this is ```sqlite3``` then a sqlite database is stored in the container ```/app``` directory.
If this is ```postgres``` then you must also set the ```POSTGRES_HOST```, ```POSTGRES_USER```, ```POSTGRES_DB```, and ```POSTGRES_PORT``` variables.

### ```SQLITE_DB_PATH```
Optional path to the SQLITE database if using the sqlite3 driver.

### ```HEADERS_FROM_EMAIL```
Email address to include in request headers from Insight when contacting APIs. This should be an email of the bot admin for API managers to contact for service abuse or issues.

### ```DISCORD_TOKEN```
The Discord bot token from [Discord Apps](https://discordapp.com/developers/applications/me).

### ```CCP_CLIENT_ID```
The CCP application ID obtained from [EVE App Developers](https://developers.eveonline.com/applications/create).

### ```CCP_SECRET_KEY```
The CCP application secret key obtained from [EVE App Developers](https://developers.eveonline.com/applications/create).

### ```CCP_CALLBACK_URL```
The CCP application callback URL obtained from [EVE App Developers](https://developers.eveonline.com/applications/create).

### ```CLEAR_TOKEN_TABLE_ON_ERROR```
Set to ```TRUE``` to drop the token table if Insight is unable to read it with the stored encryption key. 
Set to ```FALSE``` to make Insight exit with error without modifying the token table when unable to read it.

### ```DISCORDBOTS_APIKEY```
Optional DiscordBots API key for server count metrics and stats.

### ```INSIGHT_ENCRYPTION_KEY```
Optionally set the encryption key through this env var if you don't plan on storing the encryption key through a Docker volume. 
Leaving this value blank will look for the key written to ```/app``` and create it if it does not exist. 

### ```INSIGHT_STATUS_CPUMEM```
Set to ```TRUE``` to update bot "Watching" activity with CPU and memory stats, otherwise don't display this metric.

### ```INSIGHT_STATUS_FEEDCOUNT```
Set to ```TRUE``` to update bot "Watching" activity with feed count stats, otherwise don't display this metric.

### ```INSIGHT_STATUS_TIME```
Set to ```TRUE``` to update bot "Watching" activity with delay / time stats, otherwise don't display this metric.

### ```LIMITER_*``` variables
The following are all rate limiter variables and modify the rate limiting behavior of Insight based on buckets.

All values are integers. See https://wiki.eveinsight.net/en/user/limits for more info.

* LIMITER_GLOBAL_SUSTAIN_TICKETS
* LIMITER_GLOBAL_SUSTAIN_INTERVAL
* LIMITER_GLOBAL_BURST_TICKETS
* LIMITER_GLOBAL_BURST_INTERVAL
* LIMITER_DM_SUSTAIN_TICKETS
* LIMITER_DM_SUSTAIN_INTERVAL
* LIMITER_DM_BURST_TICKETS
* LIMITER_DM_BURST_INTERVAL
* LIMITER_GUILD_SUSTAIN_TICKETS
* LIMITER_GUILD_SUSTAIN_INTERVAL
* LIMITER_GUILD_BURST_TICKETS
* LIMITER_GUILD_BURST_INTERVAL
* LIMITER_CHANNEL_SUSTAIN_TICKETS
* LIMITER_CHANNEL_SUSTAIN_INTERVAL
* LIMITER_CHANNEL_BURST_TICKETS
* LIMITER_CHANNEL_BURST_INTERVAL
* LIMITER_USER_SUSTAIN_TICKETS
* LIMITER_USER_SUSTAIN_INTERVAL
* LIMITER_USER_BURST_TICKETS
* LIMITER_USER_BURST_INTERVAL

### ```METRIC_LIMITER_MAX```
Max lines to display in ticket limiter overview output.

### ```REDIS_HOST```
The Redis hostname for caching.

### ```REDIS_PORT```
The Redis port for caching.

### ```REDIS_PASSWORD```
The Redis password for caching.

### ```REDIS_DB```
The Redis DB for caching.

### ```REDIS_PURGE```
If ```TRUE``` the Redis DB is purged on every Insight start.

### ```REDIS_TIMEOUT```
Redis connection timeout.

### ```REDIS_SSL```
If set to ```TRUE```, require SSL connections to the Redis database.

### ```POSTGRES_HOST```
The DNS hostname of the Postgres cluster.

### ```POSTGRES_USER```
The postgres user that has read/write access to the database.

### ```POSTGRES_PASSWORD```
The target postgres user password.

### ```POSTGRES_DB```
The target database name residing on ```POSTGRES_HOST```.

### ```POSTGRES_PORT```
The target database port. Defaults to ```5432```.

### ```INSIGHT_ADMINS```
Discord user IDs of users who will have Insight admin permissions separated by ";".

### ```REIMPORT_*``` variables
The following variables control when to reimport data from ESI. All values are integers.
* REIMPORT_LOCATIONS_MINUTES
* REIMPORT_TYPES_MINUTES
* REIMPORT_GROUPS_MINUTES
* REIMPORT_CATEGORIES_MINUTES
* REIMPORT_STARGATES_MINUTES
* REIMPORT_SYSTEMS_MINUTES
* REIMPORT_CONSTELLATIONS_MINUTES
* REIMPORT_REGIONS_MINUTES
* REIMPORT_CHARACTERS_MINUTES
* REIMPORT_CORPORATIONS_MINUTES
* REIMPORT_ALLIANCES_MINUTES

### ```WEBSERVER_ENABLED```
If set to ```TRUE``` the callback listener will operate as a webserver and open the port set by ```WEBSERVER_PORT``` to receive callbacks.
If set to ```FALSE``` the webserver component is not started.

### ```WEBSERVER_INTERFACE```
Webserver interface IP or hostname.

### ```WEBSERVER_PORT```
The webserver port.

### ```CALLBACK_REDIRECT_SUCCESS```
Callback URL to redirect to after successful callback.


# License
View license for [Insight](https://github.com/EVEInsight/Insight/blob/master/LICENSE.md).

## CCP Copyright Notice
EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. 

CCP hf. has granted permission to **Insight** to use EVE Online and all associated logos and designs for promotional and information purposes on its website but does not endorse, and is not in any way affiliated with, **Insight**. CCP is in no way responsible for the content on or functioning of this website, nor can it be liable for any damage arising from the use of this website.
