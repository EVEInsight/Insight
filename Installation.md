# Insight v0.11.0 Installation Guide

## Executable Requirements

### Windows
* Windows 10 or Windows Server 2016
### Linux
* GLIBC 2.19 or greater
    * Run ```ldd --version``` to check
### Mac
* Not supported
    * Must build from [source](https://github.com/Nathan-LS/Insight/wiki/Installation)

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
6. Go to [CCP Developer](https://developers.eveonline.com/applications/create) and create a new app with the following settings:
    * **Connection Type** = Authentication & API Access
    * **Requested Scopes List**
        * esi-characters.read_contacts.v1
        * esi-corporations.read_contacts.v1
        * esi-alliances.read_contacts.v1
    * For the **callback**, enter ```https://insight.nathan-s.com/Insight/callback``` if you don't plan on personally hosting a callback landing page.
    Insight does not utilize a callback listener for simplicity so the user must manually copy and paste their returned callback URL into Discord.
    Feel free the host the contents of /callback/index.html and modify the callback to point to your own landing page.
7. Create your new CCP App and copy paste the **Client ID**, **Secret Key**, and **Callback URL** into the appropriate sections in your **config** file.
8. Save your config file and rename it from ```default-config.ini``` to ```config.ini```.
9. Run **Insight.exe** on Windows or **Insight** on Linux.
Note: On first run, Insight will begin importing data from the SDE database. This could take around 10 minutes so don't close the application.
10. See [inviting your bot](#inviting-your-bot) to invite your newly created bot to your Discord server.

## Updating
1. Download the latest Insight release archive for your operating system from [github](https://github.com/Nathan-LS/Insight/releases).
1. Extract the archive overwriting all files in your current EVE-Insight directory except **Database.db** and **config.ini**.


## Inviting your bot
1. Find your Discord application's id from [Discord Apps](https://discordapp.com/developers/applications/me).
2. Edit this URL to include your app's client ID:
    ```
    https://discordapp.com/api/oauth2/authorize?client_id=YourClientIDHere&permissions=149504&scope=bot
    ```