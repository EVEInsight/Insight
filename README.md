# Insight Rewrite
A complete rewrite of the original Insight Bot. The Insight rewrite code has been slowly worked on over the last few weeks
and is nearly ready. Note: This is a WIP and feedback is appreciated.

The original hosted Insight bot will still run until the rewrite is complete. 

When the rewrite is complete the original hosted Insight bot will be discontinued and be replaced with
a new hosted Discord bot running the rewrite code.


To use this bot you may self host and create a Discord application with this code or use the provided
link to invite an Insight bot I personally host to your server. The bot is designed to be capable of running on multiple 
Discord servers, providing a separate individual experience for each. I.e. It's wasteful to run a separate
individual Insight application for each server. 

https://discordapp.com/oauth2/authorize?&client_id=379780340098662412&scope=bot

Note: This Discord Application link is running the Insight Main (original) branch
while this rewrite branch is finalized.


# Description
The original Insight bot requires a much needed code redesign.
At the time of the project's creation I was unfamiliar with asnycio and as a result, 
much of the original code was heavily unoptimized, confusing, and fractured.

The bot started off as a basic utility bot without a clear set of functions or features and as features were coded in
the code grew to be unmanageable and slow.


The most popular utility of the original Insight project appeared to be live KM feeds, and as a result the Insight rewrite
will specialize entirely in various KM feeds to see basic live entity(alliance/corp/pilot) and capRadar(tracking and reporting of nearby capitals)
with an easier interface for commands.

#Features
* Feeds
    * Entity tracking  
        * Reports destroyed ships participated in or belonging to a set of entities (alliance,corp,pilot).
    * Cap radar
        * Reports supercapital, carrier, or blops activity in a LY radius of a selected system.
        * Ignore lists
            * API synchronizable standings to ignore friendly supers that may be used within the radius.
        * Alerts 
            * Optional @everyone and @here alerts if the radar detects a hostile capital/super recently involved in a KM.
            Example: KM occurred within the last minute so a supercapital could still be within the vicinity.
    * Discord embedded visuals
        * Visually appealing discord embeds instead of plain text messages for organized and functional information.
            * Multiple link buttons to quickly access more information through Dotlan or zKillboard.
                * Links for system related, pilot, detailed km in the case of Entity tracking feeds.
                * Links for attacking super/capital pilot zK, detailed zK report, premade Dotlan jump routes from base system to km system for titans/supers, carriers, and blops in the case of capRadar.
            * Relevant embedded images
                * Logos, portraits, destroyed ship in the case of Entity feeds.
                * Highest valued attacking ship (titan/super,blops) image and corporation/alliance logo.  
            * Formatted text
                * Description and text are formatted with Discord code blocks for alignment and layout spacing not possible with normal Discord text messages.
            * Adjusted timestamp footer
                * Shows the time occurrence of a KM localized to every Discord client.
* Preconfigured Feeds
    * Constant addition of preconfigured feeds without the need for configuration.
        * Supercapital losses only
            * A feed that only shows supercapitals destroyed.
        * Abysmal losses only 
            * A feed that only shows ships destroyed in abyssal space.
        * Freighter ganks
            * Shows only freighters destroyed in high security space not to war decelerations.
        * Universal supercarrier activity
            * A capRadar feed that shows all supercapital activity within the game regardless of standing or location.        
* Simpler Commands 
    * Removal of chained, hard to remember commands. All available commands will be one word.
        * Example command to create a new feed:
            * Before: "!csettings !capRadar !create" or "!csettings !enfeed !create" 
            * After: "!create"
        * Example command to remove a feed:
            * Before: "!csettings !capRadar !delete" or "!csettings !enfeed !delete"
            * After: "!delete"
    * Nested options
        * Running commands will present you with options, exact descriptions, and a selection to chose one.
    * No arguments
        * Commands no longer require confusing arguments. Running a command will present you with options and allow you to select one.
        
* Faster, rewritten backend
    * Responsible, restricted threading. Less threads but more specialized and responsibly programed.
        * The original project was written with a disregard to the number of threads and the danger of using asyncio and too many threads together.
        * Rewrite uses only 3 threads for work.
            * A zk KM pulling/db insertion thread.
            * A thread that pushes a KM object to all running feed channels and checks filters / criteria.
            * The Discord asnycio event loop to handle commands and asynchronous pushing of matched KM objects to channels.
    * No requerying of the database for km information.
        * KM objects are represented as SQLAlchemy objects and linked information is all eagerly loaded.
        * From the second KMs are inserted into the database the underlying KM SQLAlchemy instance is passed to all channels without the need
        of a requery for each individual channel compared to the original which queried the entire database for each channel with expensive joining.
    * Better scaling
        * Adding more feeds and servers will not impact the bot's ability to run
            * As more servers and feeds were added with the original branch, more
            threads and MySQL queries would be hitting the database. In most
            cases this would slow the bot and MySQL down to a crawl and KMs
            would be displayed hours after they initially occurred.
            * In rewrite, the number of threads and ongoing queries remains constant
            so Insight is only limited by Discord's 100 server limit per bot application.
                * Add as many feeds as you like! Rewrite can handle it without stalling!
                
         
