# Insight v1.6.0 Installation Guide
This guide is for users who downloaded an Insight binary package from [releases.](https://github.com/Nathan-LS/Insight/releases)
If you are running Insight from source, see [source installation guide.](https://wiki.eveinsight.net/install/source)
If you are using Docker, please see [Docker setup guide](https://hub.docker.com/r/nathanls/insight)
## Binary Executable Requirements

### Windows
* Windows 10 or Windows Server 2016
* At least 1GB RAM
### Linux
* At least 1GB RAM
* GLIBC 2.19 or greater
    * Run ```ldd --version``` to verify
    * The Linux binary is built using Debian 8 so just about anything besides older versions of CentOS should work.
### Mac
* Binary not supported
    * Must build from [source](https://wiki.eveinsight.net/install/source)

## Installing
1. Extract the latest Insight [release](https://github.com/Nathan-LS/Insight/releases) archive.
2. Navigate to the **EVE-Insight** folder after extracting.
3. Find and open the 'default-config.ini' file with a text editor.
4. Go to [Discord Developer](https://discordapp.com/developers/applications/me) and create a **New App**.
    * No **Redirect URL** is required.
    * After creating a new app, edit your app and click **Create a Bot User**.
    * Ensure the **Public Bot** checkbox is enabled and the **Require OAuth2 Code Grant** is disabled.
5. Copy your Discord application's **Token** into the config file under the section [discord]. Your config file section should look
like this:
    ```
    [discord]
    token = YourDiscordAppTokenGoesHereWithoutQuotes
    ;required - Create a new Discord app at https://discordapp.com/developers/applications/me and set token to your App's token
    ```
6. Go to [CCP Developers](https://developers.eveonline.com/applications/create) and create a new app with the following settings:
    * **Connection Type** = Authentication & API Access
    * **Requested Scopes List:**
        * esi-characters.read_contacts.v1
        * esi-corporations.read_contacts.v1
        * esi-alliances.read_contacts.v1
    * **Callback** = ```https://insight.nathan-s.com/Insight/callback``` if you don't plan on personally hosting a callback landing page.
        * Insight does not utilize a callback listener for simplicity so the user must manually copy their returned callback URL into Discord.
    Feel free to host the contents of /callback/index.html and modify the callback to point to your own landing page. The above URL is hosted on Github and directs users to the contents of ```Insight/callback/index.html```.
7. Create your new CCP App and copy the **Client ID**, **Secret Key**, and **Callback URL** into the appropriate sections in your **config** file.
8. Save your config file and rename it from ```default-config.ini``` to ```config.ini```.
9. Run **Insight.exe** on Windows or **Insight** on Linux.
Note: On the initial run Insight will begin importing data from the SDE database. Importing static data could take upwards of 10 minutes so don't close the application.
10. See [inviting your bot](#inviting-your-bot) to invite your newly created bot to your Discord server.

## Updating
1. Download the latest Insight release archive for your operating system from [Github releases](https://github.com/Nathan-LS/Insight/releases).
2. Extract the archive, overwriting all files in your current EVE-Insight directory except **Database.db** and **config.ini**.
    * Be careful to never lose your **config.ini** file as the token column encryption secret is stored in it.

## Inviting your bot
1. Find your Discord application's id from [Discord Apps](https://discordapp.com/developers/applications/me).
2. Edit this URL to include your app's client ID:
    ```
    https://discordapp.com/api/oauth2/authorize?client_id=YourClientIDHere&permissions=149504&scope=bot
    ```
### or
1. A link is provided when Insight starts. Check the program console and copy down the **Invite Link**.