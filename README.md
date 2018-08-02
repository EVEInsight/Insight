# Insight v1.0.0
Insight provides EVE Online killmail streaming for Discord. Insight can stream personal or corporate killboards, detect supercapitals with a proximity radar, and more!
Killmails and intel are presented in visually appealing Discord embedded objects consisting of relevant links and images to quickly identify important information.

The bot features an intuitive interface for creating, modifying, and managing isolated feed configurations through simple commands and text dialog. All bot functionality is accessible through [documented commands](https://github.com/Nathan-LS/Insight/wiki/Commands) with no hardcoding or complicated configuration steps.

[Invite Insight](#links) to your Discord server and run ```!create``` to begin setting up a feed!

# Links
[![Discord Bots](https://discordbots.org/api/widget/463952393206497290.png)](https://discordbots.org/bot/463952393206497290)
* Insight (with preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=149504&scope=bot)
* Insight (without preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=0&scope=bot)

Insight is available publicly hosted(main branch) for invites directly to Discord servers. 
[Binary releases](https://github.com/Nathan-LS/Insight/releases) or a [source installation guide](https://github.com/Nathan-LS/Insight/wiki/Installation) are available if you wish to host Insight yourself.

If you have any questions, suggestions, or bug reports, feel free to drop by the [project support server.](https://discord.gg/Np3FCUn)

# Table of contents
- [Insight v1.0.0](#insight-v100)
- [Links](#links)
- [Table of contents](#table-of-contents)
- [Feature Overview](#feature-overview)
- [Gallery](#gallery)
- [Commands](#commands)
- [Permissions](#permissions)
- [Getting started](#getting-started)
  * [Entity Feed](#entity-feed)
  * [Capital Radar Feed](#capital-radar-feed)
- [Installation](#installation)
- [Credits](#credits)
- [Licenses](#licenses)
- [Rewrite and project history](#rewrite-and-project-history)
    

# Feature Overview
* Entity feeds ideal for personal, corporate, or alliance killboard streaming.
* Capital radar feeds ideal for tracking hostile incursions into friendly space, hunting expensive targets within jump range, or detecting capital escalations in real time.
* Preconfigured feeds offering custom spins such as: Alliance Tournament system feed, npc officer hunter, AT ship radar, and more!
* Embedded visuals to present mails with artful color sidebars, hyperlinks, and images.
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

![](https://github.com/Nathan-LS/Insight/raw/dev/docs/images/overview_new.png)

# Commands
Detailed command information is available in the [commands wiki.](https://github.com/Nathan-LS/Insight/wiki/Commands)

When in doubt, run ```!help```. The ```!help``` command guides you to every possible command, feature, and modifiable option.

# Permissions
The preconfigured role invite [link](#links) creates a server role with necessary permissions already assigned. Using the invite [link](#links) without preconfigured roles requires manual permission configuration.

In intended feed channels the bot requires the following permissions:

| Permission | Reason |
|---|---|
| Read Messages | Allows the bot to read command events.|
| Send Messages | Allows the bot to communicate and display prompts to users running commands.|
| Embed Links   | Allows the bot to post Discord embedded content containing images (ship renders, player portraits, corp/alliance logos) and hyperlinks (zKillboard and Dotlan).
| Mention Everyone | Allows the bot to optionally mention @here or @everyone if configured to do so for alerts in capital radar feeds.


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
## Capital Radar Feed
This quick start guide will help you set up a radar feed for tracking supercapital activity within
12 lightyears of our base system, Jita.
1. Begin by inviting Insight to your Discord server using one of the provided [links](#links).
2. Ensure Insight has the correct [permissions](#permissions) in the intended feed channel.
3. Run the command:
``` !create``` and select 'Capital Radar'.
4. The bot will ask us for the name of a base system. In our example case, enter ```Jita```.
5. Next, we will be asked for the maximum lightyear range from Jita we wish to track targets. Enter ```12```
or whichever range you prefer.
6. We will be shown a few prompts asking if we wish to track black ops, regular capitals, and supers. You 
can track all of these groups or a subset as in our case. Answer ```no``` to tracking blops
and normal capitals, selecting ```yes``` to track supercapitals.
7. A prompt will ask for the maximum mail age in minutes. Enter ```20``` as a reasonable limit or some other integer.
8. The feed service is now fully configured! You can manage settings, add or remove base systems, and more 
by running the ```!settings``` command. Radar feeds feature an optional API synchronized list of allies
to blacklist from appearing on the radar, accessible by the ```!sync``` command.

# Installation
Packaged binaries are available for Windows and Linux under [releases](https://github.com/Nathan-LS/Insight/releases). Binary releases are the simplest way 
to host your own Insight copy. Follow the instructions in ```Installation.md```, edit ```default-config.ini``` and you are ready to go! There are no additional downloads or package management systems to deal with.

If you wish to run the latest Insight branch from source you will need a Python 3 interpreter and 
the packages in ```requirements.txt```. The [wiki](https://github.com/Nathan-LS/Insight/wiki/Installation) contains a detailed guide for 
source installation using a Linux operating system.

# FAQ
    
# Credits
* [Fuzzwork](https://www.fuzzwork.co.uk/) - Provides SQLite database conversions of CCP's SDE which Insight references on initial loading.
* [zKillboard](https://github.com/zKillboard/zKillboard) - Provides a centralized database of killmails for the game EVE Online.
    * [zKillboard RedisQ](https://github.com/zKillboard/RedisQ) - A websocket alternative used to pull mails.
* [CCP Games](https://www.ccpgames.com/)
    * [EVE Swagger Interface](https://esi.evetech.net/ui/) - EVE's official API, used by Insight to lookup names, information, and utilize access tokens.
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

Over the last few months I gained a better understanding of asynchronous programming and decided to rewrite the Insight project. This rewrite would have the only goal of providing better, simpler, killmail feed streaming/intel.

I present the Insight rewrite project in the hopes that it's useful and enjoyed by the EVE community.