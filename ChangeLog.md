# v1.0.0
v1.0.0 is the initial public release/announcement of the Insight Project. This rewrite of the bot was in progress for the past month and focused on redesigning the original
project with a clear set direction and purpose. This release of Insight is feature-complete and stable.
## Changes
* Direct Message remove a token from channel option
    * Replaced channel id with channel_name(server_name)
* Added ChangeLog.md to git and binary archive file.

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