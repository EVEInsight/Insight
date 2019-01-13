# Insight v1.4.0
Insight provides EVE Online killmail streaming for Discord. Insight can stream personal or corporate killboards, detect supercapitals with a proximity radar, and more!
Killmails and intel are presented in Discord rich embeds containing relevant links and images to quickly identify important information.

This bot features an intuitive interface for creating, modifying, and managing isolated feed configurations through simple commands and text dialog. All bot functionality is accessible through [documented commands](#commands) with no hardcoding or complicated configuration steps.

[Invite Insight](#links) to your Discord server and run ```!create``` to begin setting up a feed!

# Links
[![Discord Bots](https://discordbots.org/api/widget/463952393206497290.svg)](https://discordbots.org/bot/463952393206497290)
* **Insight** (with preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=149504&scope=bot)
* **Insight** (without preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=0&scope=bot)

Insight is available publicly hosted for invites directly to Discord servers.
 
See [hosting Insight](#hosting-insight) if you are interested in hosting your own copy of Insight.

If you have questions, suggestions, or bug reports feel free to drop by the [project support server.](https://discord.gg/Np3FCUn)

# Table of contents
- [Links](#links)
- [Table of contents](#table-of-contents)
- [Feature Overview](#feature-overview)
- [Gallery](#gallery)
- [Commands](#commands)
- [Permissions](#permissions)
- [Getting started](#getting-started)
  * [Entity Feed](#entity-feed)
  * [Radar Feed](#radar-feed)
- [Branch overview](#branch-overview)
- [Hosting Insight](#hosting-insight)
  * [Docker](#hosting-insight)
  * [Binaries](#hosting-insight)
  * [Source](#hosting-insight)
- [FAQ](#frequently-asked-questions)
- [Credits](#credits)
- [Licenses](#licenses)
- [Rewrite and project history](#rewrite-and-project-history)
    

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
   
# Gallery

![](https://github.com/Nathan-LS/Insight/raw/dev/docs/images/overview_entity.png)

![](https://github.com/Nathan-LS/Insight/raw/dev/docs/images/overview_radar.png)

![](https://github.com/Nathan-LS/Insight/raw/dev/docs/images/overview_pwatch.png)

# Commands
When in doubt, run ```!help```. The ```!help``` command guides you to every possible command, feature, and modifiable option.

Commands can be prefixed with either ```!```, ```?```, or ```@Insight``` by default. You can add or remove server-wide command prefixes via the ```!prefix``` command.

| Command | Description |
|---|---|
| !about | Display Insight credits, version information, and bot invite links. |
| !admin | Access the Insight admin console to execute administrator functionality. |
| !create | Begin setting up a new feed service in this channel. Alias: **!new** |
| !dscan | Coming soon! |
| !8ball | Shake the 8ball. |
| !help | Display command information and prefixes. |
| !lock | Lock a feed service from being modified by users without certain Discord channel roles. |
| !prefix | Manage server-wide command prefixes for this bot. |
| !quit | Close and shut down the Insight application service. |
| !remove | Delete the currently configured feed service in this channel. |
| !settings | Modify feed settings and behavior. Alias: **!config** |
| !start | Start/resume a channel feed from being paused. |
| !status | Display information about the currently running feed. |
| !stop | Pause a channel feed. |
| !sync | Manage contact EVE tokens for a radar or proximity watch feed. Contact token syncing allows you to ignore allies in tracked ships from appearing as potential targets. |
| !unlock | Unlock a feed service to allow any Discord channel user to modify feed configuration. |

More detailed command information is available in the [commands wiki.](https://github.com/Nathan-LS/Insight/wiki/Commands)

# Permissions
The preconfigured role invite [link](#links) creates a server role with necessary permissions already assigned. Using the invite [link](#links) without preconfigured roles requires manual permission configuration.

In intended feed channels the bot requires the following permissions:

| Permission | Reason |
|---|---|
| Read Messages | Allows the bot to read command events.|
| Send Messages | Allows the bot to communicate and display prompts to users running commands.|
| Embed Links   | Allows the bot to post Discord rich embed content containing images (ship renders, player portraits, corp/alliance logos) and hyperlinks (zKillboard and Dotlan).
| Mention Everyone | Allows the bot to optionally mention @here or @everyone for optional alerts.

# Getting started
## Entity Feed
This quick start guide will help you set up an alliance killboard tracking feed.
1. Begin by inviting Insight to your Discord server using one of the provided [links](#links).
2. Ensure Insight has the correct [permissions](#permissions) in the intended feed channel.
3. Run the command:
``` !create``` and select 'Entity Feed'.
4. Type in the name of an entity you wish to track. In this case, 
let's create a feed that tracks alliance Brave Collective. Type the name ```Brave Collective``` or whichever
entity you wish to track.
5. Select the display mode if you want to display kills, losses, or both for Brave Collective.
6. The feed service is successfully configured and running! You should start to see activity whenever
a tracked entity participates in PvP. You can now run the command ```!settings``` to add or remove entities
in your feed. If you wish to remove the feed, run ```!remove```.

## Radar Feed
This quick start guide will help you set up a radar feed for tracking supercapital activity within 12 light-years of our base system, Jita.
1. Begin by inviting Insight to your Discord server using one of the provided [links](#links).
2. Ensure Insight has the correct [permissions](#permissions) in the intended feed channel.
3. Run the command:
``` !create``` and select 'Radar'.
4. The bot will ask for the name of a base system. In our example case, enter ```Jita```.
5. Next, we will be asked for the maximum light-year range from Jita we wish to track targets. Enter ```12```
or whichever range you prefer.
6. We will be shown a few prompts asking if we wish to track black ops, regular capitals, and supers. You 
can track all of these groups or a subset as in our case. Answer ```no``` to tracking blops
and normal capitals, selecting ```yes``` to track supercapitals.
7. A prompt will ask for the maximum mail age in minutes. Enter ```20``` as a reasonable limit or some other integer.
8. The feed service is now fully configured! You can manage settings, add or remove base systems, and more 
by running the ```!settings``` command. Radar feeds feature an optional API synchronized list of allies
to blacklist from appearing on the radar, accessible by the ```!sync``` command.

# Branch overview
| Branch | Purpose |
|---|---|
| master | Stable with latest features. The [public bot](#links) runs this branch. |
| development | Latest unstable features. You can invite the [public experimental bot](https://discordapp.com/api/oauth2/authorize?client_id=477314845608378369&permissions=149504&scope=bot), but there are no guarantees of uptime or stability. |
| dev | Deprecated branch. |
| experimental | Deprecated branch. |

# Hosting Insight
There are three ways to run and host Insight yourself if you do not wish to use the [public bot](#links).
#### [Docker](https://hub.docker.com/r/nathanls/insight/)
The recommended and easiest method to host Insight. Images are automatically built on new commits.
1. Create and navigate to a directory where you wish to store Insight configuration, logs, and database.
2. Pull and run the image. This command will pull the stable Docker Insight image and initialize the config files in your current directory.
    ```
    $ docker run --name insight-container-name -it --rm -v ${PWD}:/app nathanls/insight --docker-init
    ```
3. Edit ```default-config.ini``` and populate your configuration values in accordance with the [Configuring Insight](https://hub.docker.com/r/nathanls/insight/) section. Rename this file to ```config.ini```.
4. Keep the image up to date by checking for updates and then starting Insight: 
    ```
    $ docker pull nathanls/insight && docker run --name insight-container-name -it --rm -v ${PWD}:/app nathanls/insight
    ```
See [Insight on Docker Hub](https://hub.docker.com/r/nathanls/insight/) and [Docker docs](https://docs.docker.com/) for more information about using Docker.

#### [Binaries](https://github.com/Nathan-LS/Insight/releases)
Packaged binaries are available for Windows and Linux under [releases](https://github.com/Nathan-LS/Insight/releases). Executables are built with PyInstaller using the installer script in ```/scripts/PyInstaller.spec```. New binaries are built for stable point releases. Docker or Python are not required to be installed when running binary releases.

Follow the instructions in ```Installation.md```, edit ```default-config.ini``` and you are ready to go! There are no additional downloads or package management systems to deal with.

#### [Source](https://github.com/Nathan-LS/Insight/wiki/Source-Installation)
Requires a Python 3.6 interpreter (<=3.5 and >=3.7 not supported) and Docker for building dependencies.
The [wiki](https://github.com/Nathan-LS/Insight/wiki/Source-Installation) contains a detailed guide for 
source installation using a Linux operating system.

# Frequently asked questions
**How do I invite Insight to my Discord server?**

You can invite Insight to any server where you have the **Manage Server** role. Follow the [link](#links), select the server, and Insight will be invited. If you are hosting Insight yourself, the invite link will be printed in the program console on program startup. 

**What Discord permissions does Insight require?**

Insight requires the permissions outlined in the [permissions section.](#permissions)


**How do I set up a new feed and manage its settings?**

Creating a feed is as simple as running the command ```!create``` and following the dialog prompts to select a type.
Running the command ```!settings``` allows you to modify feed configuration and behavior.


**What's the difference between hosting Insight myself and using the publicly hosted bot?**

Functionally, there is no difference. Insight is designed to support simultaneous feeds across multiple servers with no configuration hardcoding. 
Insight provides an isolated service to each Discord channel, separate from the modification or access of other channels/servers.

Operationally, the publicly hosted bot runs on dedicated, secure hardware to provide 24/7 service and reliability. The publicly hosted bot runs the main branch and is updated, maintained, and secured seamlessly. 

**How do I run more than one feed service?**

Insight can only run one feed service per Discord channel. Create more text channels and create a feed service in each.
Note: Insight does not support feeds in direct message or conversations.


**How do I add, manage, or remove one of my previously added SSO tokens?**

Direct message the bot with the ```!sync``` command and select an option. You can always revoke tokens under [third party applications.](https://community.eveonline.com/support/third-party-applications/)



**What do all the stats mean on the bot's watching message?**

Insight keeps track of delays for service reliability. See the [wiki article](https://github.com/Nathan-LS/Insight/wiki/Color-codes-and-bot-status) for a detailed description.


**How do I host Insight myself?**

Insight runs on Windows, Linux, or Mac. See the [hosting insight](#hosting-insight) section.


**Why do I have to paste my callback url when using the !sync command?**

For installation simplicity, Insight does not utilize a callback listener. A listener would require a web server and open new security concerns. In general scenarios, authenticating with a third party website works like this:
1. Be directed to authenticate with EVE by a third-party service.
2. Login with EVE and be redirected, through a GET request, back to the service's callback landing page.
3. A running callback listener would receive the GET request and link the ```code=``` parameter of the URL to a PHP session. 

Insight follows the same procedure except for step 3. The callback URL must manually be entered by the user as Insight has no web listener or easy way to link Discord users with their tokens. Insight parses the url, extracts the authorization code, and links the token with the unique Discord user ID.


**How can I be notified of updates?**

Insight's ```Watching CPU:15% MEM:1.0GB``` status will change to ```Watching Update available```. The program console will display messages directing to the latest release.


**I have an unanswered question, want to request a feature, need help with installation, or report a bug.** 

Check out the public Discord server listed in the [links section.](#links)
# Credits
* [Fuzzwork](https://www.fuzzwork.co.uk/) - Provides SQLite database conversions of CCP's SDE referenced on initial loading.
* [zKillboard](https://github.com/zKillboard/zKillboard) - Provides a centralized database of killmails for the game EVE Online.
    * [zKillboard RedisQ](https://github.com/zKillboard/RedisQ) - A websocket alternative used to pull mails.
* [CCP Games](https://www.ccpgames.com/)
    * [EVE Swagger Interface](https://esi.evetech.net/ui/) - EVE's official API used by Insight to lookup names, information, and utilize access tokens.
* [Swagger Codegen](https://github.com/swagger-api/swagger-codegen) - An automatic API client generation tool for services utilizing Swagger definitions.

# Licenses
Insight is released under the GNU General Public License v3.0 and the full license
is available in the file ```LICENSE```. This project utilizes various Python libraries, each with their
own licensing. Insight uses data and names from the game EVE Online subject to its license
included in the file ```CCP.md```.

# Rewrite and project history
Insight development initially began in January 2018 as an introductory project in asynchronous Python programming. Originally, the bot was meant
to fill various roles such as: ship dscan intel, killmail feeds, route planning/calculations, and more. The original Insight lacked a clear focus, features were programmed in 
randomly, and the code base became bulky and confusing. The first writeup of Insight should be taken as a clear example of how not to code with Python asyncio.

Over the last few months I gained a better understanding of asynchronous programming and decided to rewrite the Insight project. This rewrite would have the only goal to provide better, simpler killmail feed streaming/intel.

I present the Insight rewrite project in the hopes that it's useful and enjoyed by the EVE community.