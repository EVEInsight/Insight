# v1.5.1
## Fixes
* Fixed an issue where the MailError log file was not being properly rotated. Retry attempts are now logged as info.
* Corrected appearance gallery URLs for derived/preconfigured feeds.
* Fixed an issue on entity and derived feeds utilizing the utility appearance where mails would not post involving a final blow from a single unknown NPC attacker.
# v1.5.0
This version of Insight is a general maintenance release addressing minor underlying issues with Insight.
## Notices
* The pyinstaller binary/executable release of Insight is no longer supported in this release and releases going forward. The pyinstaller scripts exist under ```scripts/``` if you wish to experiment with pyinstaller. Please switch to [Docker](https://hub.docker.com/r/nathanls/insight).
## New features
* A new website has been created at [eveinsight.net](https://eveinsight.net) to better market Insight and show off features to new users.
* A new wiki has been created at [wiki.eveinsight.net](https://wiki.eveinsight.net) to replace the GitHub wiki. All further wiki-related articles will be posted to this new wiki.
* Insight better handles issues and requeueing of mails if there is an issue with posting to channels. 
In the event of a permission issue or API delay/outage Insight will attempt to resend a mail with the following delays:
    * First failure: Resend attempt after 1 minute
    * Second failure: Resend attempt after 10 minutes
    * Third failure: Resend attempt after 60 minutes
    * Fourth failure: Resend attempt after 1 day
    * Further failures: Mail is discarded and logged in the ```MailError.log``` file.
## Changes
* Bumped the versions for multiple dependencies including discord.py. 
* The Docker variant runs Insight as a newly created user. Permissions are automatically updated for the database and related files by the EntryPoint script.
* Insight will better handle permission issues on killmail posting to prevent throwing too many errors at the Discord api.
* Most wiki references have been updated to the new wiki at wiki.eveinsight.net. Some miscellaneous links have been updated to eveinsight.net. 
* Improved command parsing to use thread pools instead of using resources under the asnycio event loop. 
* Added improved logging for command parsing to more easily diagnose issues with Insight sometimes not responding to commands on certain servers.
# v1.4.0
## New features
* Server-wide command prefix modification support. Users can now add and remove Insight prefixes via the **!prefix** command.
* Docker support. Insight is available to run as a Docker container with all dependencies packaged.
* Various new appearance options. Variations of the compact appearance for entity feeds and the new abbreviated appearance for all feed types.
* The new Angry NPCs feed type. This feed displays losses to solo npc ships.
* The new Abyssal PvP feed type. This new feed displays PvP activity in Abyssal space.
## Changes
* All references to the capital radar feed have been renamed to radar feed as this feed tracks more than just capital ships.
* Crash recovery support in the parent Insight parent process which can be enabled via the ```-cr``` CLI arg.
* The default configuration file has been moved to the project root directory for consistency.
* Git repo branch restructure. See README.MD file.
* Redesigned command parser to support custom prefixes.
* Increased the maximum time delta for some feed types. Supers, freighters, etc feeds are now set to 7 days instead of 3 hours. Frequent outages in ESI resulted in some mails being loaded past the 3 hour mark and thus would not be sent to feeds.
* Radar and proximity feeds will now only print the synced token notification when the underlying count of tokens changes. Previously, any modification(contact added or removed for example) of the token would trigger a notification message.
* Redesigned the **!about** command to display libraries used, special thanks, and links (bot invite, support Discord, Changelog).
* Redesigned the **!help** command to display configured prefixes and commands with the shortest length command prefix.
* Merged the NPC Officer Hunter preconfigured feed type with the radar service. The NPC Officer Hunter is now accessible by a switch in a radar feed via **!settings**. Existing feeds are automatically converted to the radar service.
## Fixes
* Fixed an issue where the Admin reset name functions would consume a large amount of memory.
* Fixed a potential memory leak when searching for entities or systems. Also added a minimum search criteria character count.
* Fixed a potential memory issue where SQLAlchemy mail objects were held longer than expected.
## Technical
* Added the lock and semaphore pool managing utility classes.
* Added a memory diagnostic logger that will log memory and reference count changes over time.
* Numerous test additions for further stability and easier debugging going forward.
# v1.3.1
## Fixes
* Fixed an issue when running Insight on computers without Git. Attempting to run Insight on a computer without Git would result in an application crash. The Insight updater now attempts to import the GitPython library within the update function and catches the error in the event of no valid Git executable.

# v1.3.0
v1.3.0 is the latest update to Insight which includes numerous backend improvements for further application stability. 
## New features
* Added a "Big Kills" feed that displays all mails valued greater than a customized minimum ISK value.
* WebSocket streaming via the ```-ws``` flag as an optional method to obtain mails.
* Framework for multiple utility type commands which will expanded upon in later updates.
* Mention modes for all feed types with customizable time limits.
* The ```!lock``` command which prevents feeds from being modified from unauthorized Discord users lacking channel permissions. [(#13)](https://github.com/Nathan-LS/Insight/issues/13)
* Option panes now use Discord rich embeds offering better experience and support for option text exceeding the 2000 character limit.
* The ```!8ball``` utility command.
* Insight can now be cleanly shut down via CTRL-C or a Discord command.
* The ```!admin``` command interface which allows Insight administrators to access the following functionality:
    * Shutdown or reboot the Insight application
    * Name resetting to clear and repopulate all cached names in the database. Characters, corporations, etc.
    * Database and log backup into zip archives.
    * Update patching (for Git installations running on the Python interpreter) and automatic reboot/reload.
* Multiple minor adjustments to visuals and text refactoring.
* Welcome message when Insight joins a new server. Insight now offers a helpful greeting to the public channel of new servers with basic command usage.
* New scripts for easier setup and installation on Linux systems.
* Numerous improvements to core stability.

## Changes
* The AT ship radar feed type has been removed. The functionality of this feed has been merged with the full Capital Radar feed service offering extended functionality. (base systems, timeouts, etc.) Existing AT feeds are automatically converted when Insight starts.
* The "currently watching" status message has been changed to include the current number of feeds.
* Insight now sends more detailed header information to zK and ESI. Including the Git URL and optional 'from' email.
* Mails less than a minute ago will output the time in seconds.
* Contact syncing now runs every 3 hours.

## Fixes
* SSO tokens randomly raising 4xx errors are not immediately dropped. ESI would sometimes raise error 400 on a valid token when the service was experiencing issues and then return 200 later. Insight now has an error counter and drops tokens after a consecutive number of error 400s.
* Some tokens would have a specific type (alliance, corp, pilot) dropped on error 403. Error 403 signals the token owner leaving the alliance or corp, no longer having access. Error 403 was raised in rare instances of service outages. Further inspection of the error message ensures these random drops do not occur.
* A race condition was fixed which allowed users to create 2 feeds in one channel with the last feed overwriting the first. 
* Insight now attempts to resend mail messages if it fails due to error 5xx or socket error.
* Fixed an issue affecting RedisQ polling and VMware based hosts.

## Technical
**Logging**
* Added the overdue logging module with extensive logging for error detection and timing delays.
* Logging now uses TimedRotatingFileHandler for saving logs into daily files.

**RouteMapper**
* Increased speed and memory optimization improvements. 

**Database**
* Database update versions are now independent of application version. This allows multiple new patches to the database per single application update. 
* Template/preconfigured feeds use SQLAlchemy ```add``` instead of```merge``` on feed initialization to improve speed.
* Add more indexes for faster object loading and searching.
* Add ```mention``` and ```mention_every``` columns to the ```discord_channels``` table to support mention modes for every channel.
* Add ```modification_lock``` bool to ```discord_channels``` table for locking channels.
* Add ```error_count``` to tokens.
* The database service connection is properly closed when Insight is shutting down.

**Startup/shutdown**
* Insight uses multiple threads on startup to load all channel feeds, offering a limited time improvement. MySQL support when? :)
* New multiprocessing parent/child model for Insight startup. Insight utilizes two processes to handle reboot and update functionality. This model uses the Python multiprocessing library so it is supported by both Windows and Linux. 
    * Parent: The parent process checks set flags on child termination to either terminate itself or create a new child process running Insight. (reboot functionality) This process also handles updating Insight Git if requested on child termination and then rebooting (forking).
    * Child: The actual Insight service which creates the asyncio event loop and runs the bot.

**Core**
* More async locking. Multiple commands cannot be in progress in a single feed. 
* Command flooding. Add delay on responding to feeds that raise too many errors or run too many commands in a minute interval.
* Permanent threads with infinite loops have been replaced by coroutines. These coroutines submit work to thread pools as needed. Example: RedisQ polling, raw json -> DB insertion, and KM filter passing have all been redesigned to run as coroutines.
* Add WebSocket support for ZK.
* RedisQ polling and discordbots threading requests have been replaced with aiohttp coroutines.
* Thread pools are properly closed before Insight shutdown.
* Updated packages in requirements.txt.
* Increased timeout on RedisQ error 429s to 5 minutes. Don't run more than Insight copy per IP address.

**Misc**
* Add ThreadPoolPause context manager utility to block threads while backups or other administrative functions occur.
* Added numerous internal exceptions to support new functionality.

# v1.2.0
## New features
* Entity feed
    * Users can now set a minimum ISK value filter. [(#11)](https://github.com/Nathan-LS/Insight/issues/14)
* Radar
    * Users can specify custom type/group tracking in addition to supers, caps, or blops. 
* Proximity watch
    * A new feed type designed to track hostile activity within systems, constellations, or regions. This feed can also detect activity within a set jump proximity of base systems.
    The feed is capable of syncing ignore lists with tokens to ignore exclusively friendly mails.
* Preconfigured
    * Added options
        * Some options available to base feeds are now optionally available for configuration in derived feeds. Examples: maximum timeout, minimum ISK value, etc.
* SDE/data
    * Market updater
        * Updates average prices on bot startup for ships.
    * Stargate/routing module
        * Gate jump distance calculation has finally arrived to Insight. The routing module calculates and caches the distance between all systems for use in gate calculations.
## Changes
* Feed creation
    * Option order should flow better when creating feeds.
* Preconfigured
    * Discontinued the Alliance Tournament system stream until next year.
* Appearances
    * All radar embeds now list the gate jump distance in the footer.
    * Radar Full appearance positioning and verbosity has been modified to reduce space and provide a cleaner interface.
    * Renamed functional appearance to utility.
    * Add truncating to ship/affiliation overviews.
## Technical
* Routing module
    * The route caching module increases the memory footprint of Insight by 500MB when all systems are loaded. Ensure your machine is capable of handling this additional requirement.
* Updated requirements.txt
* Extensive changes to visual embed variables and function calls for easier code navigation.

# v1.1.0
## New features
* Settings
    * Rich embed visual switching
        * Rich embed presentation can be modified for all feed services by using the ```!settings```->```Change visual appearance``` option. See [(#10)](https://github.com/Nathan-LS/Insight/issues/15) and [wiki.](https://github.com/Nathan-LS/Insight/wiki/Rich-Embed-Appearance)
* Preconfigured feeds
    * New capital losses feed type - Posts all super and capital losses.
## Bug Fixes 
* Token pilots who switch corps won't have their alliance contact syncing dropped if they remain in the alliance. [Commit](https://github.com/Nathan-LS/Insight/commit/80e85c218c1141701d439f191a22f008aa195793)
## Changes
* Tokens without any tracked contact type (pilot, corp, and alliance are all set to ignore) are now automatically removed from channels and deleted from the database.
* Added the ```-defer``` argument to prevent contact syncing from running when the bot starts. Contact syncing now runs on startup by default. [Commit](https://github.com/Nathan-LS/Insight/commit/795523048704225c8b20a1972720158ab6e30bc5) 
* Added a ```View tokens``` option to radar feeds to see all linked tokens in the channel. [Commit](https://github.com/Nathan-LS/Insight/commit/225e544077bb54b55eff617fe5a10a801b218a00)

# v1.0.0
v1.0.0 is the initial public release/announcement of the Insight Project. This rewrite of the bot was in progress for the past month and focused on redesigning the original
project with a clear set of direction and purpose. This release of Insight is feature-complete and stable. v1.0.0 has a few bug fixes and focuses on polishing.
## New features
* Commands
     * !status - Display information about the currently running feed.
        * The command is limited in functionality, but will eventually be updated to include more information in a future patch.
* Support for discordbots.org
    * Optionally add your Insight copy to discordbots.org using an API token in the config file.
## Changes
* Direct Message remove a token from channel option
    * Replaced channel id with channel_name(server_name)
* ZK module
    * Added error and more response code checking to prevent needlessly spamming RedisQ when there is a zk outage.
    * The bot's next delay now accounts for all 200 response codes, even if no package is returned.
* Added ChangeLog.md to git and binary archive file.
* Text dialog polishing.
* Added more documentation to the wiki.
* Added wiki clone to project repo and release archives.
## Technical
* Added a Stargate location name importer to import names from the SDE.
    * Stargate games are NULL in the mapDenormalize SDE datebase table. The SDE only lists stargate names in the invNames table so a custom function was added to import this table.

# v0.13.1
## Changes
* Merged AT system 1 and AT system 2 streams into one channel.
    * There were issues with alliance tournament systems changing so both preconfigured feeds were merged. The stream now tracks losses in the entire
    alliance tournament region instead of specific systems to catch system changes.
* Added an invalid feed catcher.
    * Insight will automatically detect and remove discontinued feeds.

# v0.13.0
## Breaking Changes/Announcements
* Insight versions below v0.12.1 will have all SSO tokens and synced contacts dropped as a result of token encryption and table restructuring. Users will have to manually add their tokens back and reassign them to intended radar feeds. 
* There are new fields in the configuration file so ensure you merge changes from ```default-config.ini``` to your ```config.ini``` file.
* 2 new required modules in ```requirements.txt```. Ensure you run ```pip install -r requirements.txt``` to update your python installation if you are running Insight from source (not needed for binary versions). 

## New Features
* SSO token encryption
     * All tokens are now encrypted using an automatically generated secret key in the configuration file. Losing or modifying this key will corrupt the token tables and prompt for a token wipe.
* New preconfigured feeds (#6) 
    * The first of many preconfigured feeds that offer fun, customized spins on entity or radar feeds. These feeds require no setup and are unchangeable for the most part. Access them with the command '!create'.
    * 8 new preconfigured feeds:
         * **Super Losses** - Derived from entity feed. This feed displays all titan or supercarrier losses.
         * **Abyssal Losses** - Derived from entity feed. This feed displays all Abyssal space losses.
         * **Excavator Losses** - Derived from entity feed. This feed displays any excavator mining drone losses.
         * **Freighter Ganks** - Derived from entity feed. This feed displays any freighter or jump freighter losses in high-security space.
         * **AT Stream PE1-R1** - Derived from entity feed. Just in time for the Alliance Tournament, this feed displays all losses in the tournament system PE1-R1.
         * **AT Stream JB-007** - Derived from entity feed. This feed displays any losses in the tournament system JB-007.
         * **Officer Hunter** - Derived from capital radar. This feed displays any killmails involving an NPC officer with routes from Jita. Make some ISK!
          * **Universal Supers** - Derived from capital radar. A capital radar feed set to track supers from Jita with unlimited range.
          * **Alliance Tournament Ship Radar** - Derived from capital radar. This feed tracks and displays universal alliance tournament/rare ship activity. Contact syncing is supported in this derived feeds.
* Mention system and rate limiting (#10)
    * Implemented an optional mention system (@here or @everyone).
    * Rate of mentions is limited to 1 @here or @everyone per channel, per 15 minutes. This limit is currently hardcoded but will likely become customizable on a per channel basis in the future. 
    * Mentions are only accessible in the base radar feed. 
         * **Capital Radar** - Mention mode is determined by the setting for the highest valued attacking ship group.

## Changes
* Contact syncing tasks now runs every 1.5 hours instead of 10 hours.
* On automated contact syncing, Insight will only post a contact updated message if there were modifications.
     * Previously, Insight would always post alert messages to radar feeds on any background syncing actions. Insight will post one initial message on the first background sync after bot startup, and further messages will be suppressed if no modifications occurred. 
     * Modifications that trigger a synced contact message to post:
          * Any new contacts or contact standing modification for a linked token.
          * Addition or removal of contact tokens to the feed service. This includes user revoked tokens as a revoked token will automatically remove itself from all associated channels.
* Removed zKillboard and Insight/Discord API delay warnings.
     * Previously, Insight would post a message to channels if it detected outages or issues with itself. 
     * Statuses are now only represented by the bot's status color:
          * **Green** - All services operational.
          * **Yellow** - zKillboard delays or outage.
          * **Red** - Abnormal delays posting visuals/messages to channel feeds caused by either Insight overloading or Discord API outages.
* Replace startup argument ```-api``` with ```-noapi```. Insight, by default, will check and import any missing items from the SDE database on startup. Start Insight with ```-noapi``` to disable the initial check. Note: You should only skip data importing in a debug environment as the bot will will behave abnormally if it is missing static data.

## Technical 
* Added custom exceptions module for simpler exception handling and returned error messages to the user.
* SQL Updater
    * v0.12.1 - Drop the following tables for restructuring:
         * contacts_alliances
         * contacts_corporations
         * contacts_characters
         * discord_tokens
         * tokens
    * v0.10.1 - Adds the column ```template_id``` to the following tables:
         * discord_enFeed
         * discord_capRadar
* New TemplateFeeds module
* General refactoring and removal/restructuring of reused functions.