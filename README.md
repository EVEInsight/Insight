# Insight v0.11.0
Insight is a Discord bot that provides various live killmail feeds for ships destroyed within the 
game EVE Online. Insight can track your personal, corporate, or alliance activity and display information 
in visually appealing Discord embedded objects. Insight also features a live radar feed capable of
displaying hostile capital, supercapital, or black ops activity within a lightyear radius of selected
systems. The bot is available hosted to invite directly to your server, or you can clone, set up, and host the project yourself.


# Links
* Insight (with preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=149504&scope=bot)
* Insight (without preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=0&scope=bot)
* Project Help/Support Server: [Project Support](https://discord.gg/Np3FCUn)
* Project Screenshots: [Imgur Album](https://imgur.com/a/0LIkjNc)

# Table of contents
- [Insight Project](#insight)
- [Links](#links)
- [Table of Contents](#table-of-contents)
- [Features](#features)
    - [Feeds](#feeds)
    - [Discord Embedded Visuals](#discord-embedded-visuals)
    - [Preconfigured Feeds](#preconfigured-feeds)
- [Commands](#commands)
- [Permissions](#permissions)
- [Getting Started](#getting-started)
    - [Entity Feed](#entity-feed)
    - [Cap Radar Feed](#cap-radar-feed)
- [Installation](#installation)
- [Licenses](#licenses)
    

# Features
* Feeds
    * **Entity tracking**  
        * Displays involvement (kills/losses) for tracked entities (pilot, corporation, alliance).
        * Multiple entities can be added per channel.
    * **Cap radar**
        * Reports supercapital, carrier, or blops activity in a LY radius of selected systems.
        * Ignore lists
            * Synchronize SSO standings to blacklist friendly supers from appearing in the radar feed.
        * Alerts (coming soon!)
            * Optional @everyone and @here alerts for when the radar detects a hostile capital/super recently involved in a KM.
            Example: KM occurred within the last minute so a supercapital could still be within the vicinity.
* Discord embedded visuals
    * Visually appealing Discord embedded objects for organized and functional information.
        * Multiple link buttons to quickly access useful information through Dotlan or zKillboard.
            * Links for system, related, pilot, detailed km in entity feeds.
            * Links for attacking super/capital pilot zK, detailed zK report, and premade Dotlan jump routes from base system for differing ship classes in capRadar feeds.
        * Relevant embedded images
            * Logos, portraits, destroyed ship in entity feeds.
            * Highest valued attacking ship image and corporation/alliance logo in capRadar feeds.  
        * Formatted text
            * Description and text are formatted with Discord code blocks for easier reading.
        * Adjusted timestamp footer
            * Shows the time occurrence of a KM localized to every Discord client.
* Preconfigured Feeds (coming soon!)
    * Constant addition of fun, preconfigured feeds without the need for configuration.
        * Supercapital losses only
            * A feed that only shows supercapitals destroyed.
        * Abyssal losses only 
            * A feed that only shows ships destroyed in Abyssal space.
        * Freighter ganks
            * Shows only freighters destroyed in high security space not to war decelerations.
        * Universal supercarrier activity
            * A capRadar feed that shows all supercapital activity within the game regardless of standing or location.       
# Commands
To see detailed command information, see [commands wiki](https://github.com/Nathan-LS/Insight/wiki/Commands)
or run the command ```!help```.

# Permissions
An overview of required Discord permissions for the bot to function. 

The preconfigured bot invite [link](#links) creates a server role with these permissions after which you assign the 
role to intended feed channels. Using the invite [link](#links) without preconfigured roles requires manual 
configuration of the following permissions.

In intended feed channels the bot requires the following permissions:

| Permission | Reason |
|---|---|
| Read Messages | Allows the bot to access the channel and read command events.|
| Send Messages | Allows the bot to communicate and display prompts to users running commands.|
| Embed Links   | Allows the bot to post Discord embedded content containing images (ship renders, player portraits, corp/alliance logos) and hyperlinks (zKillboard and Dotlan).
| Mention Everyone | Allows the bot to optionally mention @here or @everyone if configured to do so for alerts in capRadar feeds.


# Getting started
### Entity Feed
This quick start guide will help you set up an entity feed to track both kills and losses for an alliance.

1. Begin by inviting Insight to your Discord server using one of the provided [links](#links).
2. Ensure Insight has the correct [permissions](#permissions) in the intended feed channel.
3. Run the command:
``` !create``` and select 'Entity Feed'.
4. Type in the name of an entity you wish to track. In this case, 
let's create a feed that tracks alliance Brave Collective. Type the name ```Brave Collective``` or whichever
entity you wish to track.
5. Select the display mode if you want to display kill, losses, or both for Brave Collective.
6. The feed service is successfully configured and running! You should start to see activity whenever
a tracked entity participates in PvP. You can now run the command ```!settings``` to add or remove entities
in your feed. If you wish to remove the feed, run ```!remove```.
### Cap Radar Feed
This quick start guide will help you set up a cap radar feed for tracking supercapital activity within
12 LYs of our base system, Jita.
1. Begin by inviting Insight to your Discord server using one of the provided [links](#links).
2. Ensure Insight has the correct [permissions](#permissions) in the intended feed channel.
3. Run the command:
``` !create``` and select 'Cap Radar'.
4. The bot will ask us for the name of a base system. In our example case, enter ```Jita```.
5. Next, we will be asked for the maximum lightyear range from Jita we wish to track targets. Enter ```12```
or whichever ly range you wish.
6. We will be shown a few prompts asking if we wish to track black ops, regular capitals, and supers. You 
can track all of these groups or a subset as in our case. Answer ```no``` to tracking blops
and normal capitals, selecting ```yes``` to track supercapitals.
7. A prompt will ask for the maximum KM age in minutes. Enter ```20``` as a reasonable limit or some other integer.
8. The feed service is now fully configured! You can manage settings, add or remove base systems, and more 
by running the ```!settings``` command. Cap radar feeds feature an optional API synchronized list of allies
to blacklist from appearing on the radar, accessible by the ```!sync``` command.

# Installation
Packaged executables are available for Windows and Linux under [releases](https://github.com/Nathan-LS/Insight/releases).
Edit the ```default-config.ini``` file and run! See ```Installation.md``` for installation and upgrade instructions.

If you instead wish to run Insight from source, you need a Python 3 interpreter and 
the packages in ```requirements.txt```. The [wiki](https://github.com/Nathan-LS/Insight/wiki/Installation) contains a detailed guide for 
source installation using a Linux operating system.
    
# Credits
* [Fuzzwork](https://www.fuzzwork.co.uk/) - Provides SQLite database conversions of CCP's SDE which Insight references on initial loading.
* [zKillboard](https://github.com/zKillboard/zKillboard) - Provides a centralized database of killmails for the game EVE Online.
    * [zKillboard RedisQ](https://github.com/zKillboard/RedisQ) - A websocket alternative Insight uses to pull KMs from in real time.
* [CCP Games](https://www.ccpgames.com/)
    * [EVE Swagger Interface](https://esi.evetech.net/ui/) - EVE's official API, used by Insight to lookup names, information, and utilize access tokens.
* [Swagger Codegen](https://github.com/swagger-api/swagger-codegen) - An automatic API client generation tool for services utilizing Swagger definitions.

# Licenses
Insight is released under the GNU General Public License v3.0, and the full license
is available in the file ```LICENSE```. This project utilizes various python libraries each with their
own licensing. Insight uses data and names from the game EVE Online subject to its license
included in the file ```CCP.md```.
        
                
         
