Insight provides live killmail feeds streamed from zKillboard. Feeds can be created in any Discord text channel and can be fully customized using the ```!settings``` command. Each Discord text channel can have a maximum of 1 feed service. Feed services cannot be created in group conversations or direct messages.

# Table of contents
- [Base Feed Types](#base-feed-types)
  * [Entity](#entity)
    + [Available configuration settings](#available-configuration-settings)
  * [Capital Radar](#capital-radar)
    + [Available configuration settings](#available-configuration-settings-1)
    + [How radar filtering works](#how-radar-filtering-works)
- [Preconfigured Feeds](#preconfigured-feeds)
  * [Super losses](#super-losses)
  * [Abyssal losses](#abyssal-losses)
  * [Excavator losses](#excavator-losses)
  * [Alliance Tournament system stream](#alliance-tournament-system-stream)
  * [Freighter Ganks](#freighter-ganks)
  * [Officer Hunter](#officer-hunter)
  * [Universal supers](#universal-supers)
  * [Alliance Tournament Ship Radar](#alliance-tournament-ship-radar)
# Base Feed Types
Base feeds offer full customization and configuration editing.
## Entity 
This feed displays PvP activity for a set of tracked entities. Entities are characters, corporations, or alliances. This feed type is ideal for personal, corporate, alliance, or coalition killboard streaming. Multiple entities can be added to the entity feed to track multiple pilots, or corps.

![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/entity_k.png)

### Available configuration settings
These options are available after feed creation using the ```!settings``` command. Some of these options are defined on initial feed creation.
* Add tracked entities
     * Prompts to search for an entity by name. After searching, Insight will display a list of matched character, corporation, and alliance names to choose from. The user can search again or select an option to add as a tracked entity.
* Display POD(capsule) mails
     * Sets the feed to either ignore or display POD mails.
* Set kill/loss mode
     * Sets the feed to one of three modes:
          * Shows kills only
          * Show losses only 
          * Show both kills and losses
* Remove tracking
     * Remove a previously added tracked entity from the feed.
## Capital Radar 
Capital radar feeds track hostile super, capital, or blops activity within a set lightyear proximity of base systems. Radar feeds are ideal for tracking hostile incursions into friendly space, hunting expensive targets within jump range, or detecting capital escalations. Radar feeds feature an ally blacklist to ignore friendly capitals within your proximity while displaying hostile activity. Radar feeds are capable of mentioning @here or @everyone if desired.

![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/radar_recent.png)

The visual embedded object provides valuable intel such as:
* Aggressor alliance logo and ship type render.
* Overview of tracked ship types and count for a killmail.
* Location data when available. Ex: Near **Planet 5**, **Sun**, **Planet 1 Moon 5**, etc.
* Clickable Dotlan routes from your base system to target system for various ship classes. 
* zKillboard killmail link.

### Available configuration settings
Available after creation using the ```!settings``` command. Some of these options are defined on initial feed creation.
* Add or modify base systems
     * Prompts for a name and returns a list of matched systems for the user to choose from. Once selected, Insight will prompt for the lightyear radius integer to track from the system. 
     * Only killmails that occur within the lightyear radius will be posted to the channel.  
     * Multiple systems with varying lightyear ranges can be added to a single radar feed.
     * If multiple base systems exist, Insight will post the killmail if it falls within range of at least one of the systems.
     * Re-adding a previously added system allows you to modify the radius range.
* Ship group tracking and mention modes:
     * Users can select a subset or all of the following ship groups to track in a feed. The mention mode and displayed visual is determined by the highest valued attacking ship group after filtering is applied. Mention limit is: max of 1 @here or @everyone per feed/15 minutes to avoid spam.
     * Ship groups:
          * Supercarrier and titan
          * Regular capital (FAX, dread, carrier, Rorqual)
          * Black ops battleship
     * Available mention modes for each group:
          * No mention
          * @here
          * @everyone 
* Set maximum age
     * Sets the maximum delay, in minutes, that mails will be posted to the feed. Fetched mails occurring more than the set age will not be pushed to the channel. 
* Remove a base system
     * Insight will prompt the user to remove a base system from the feed.
* Manage feed sync settings
     * Same as ```!sync``` command. This selection brings up options for syncing EVE contacts to the feed ignore blacklist. See [command !sync documentation for more information.](https://wiki.eveinsight.net/user/commands#sync)

### How radar filtering works
1. Insight receives a mail and determines the number of minutes ago it occurred. Ignore if delay exceeds the radar set max age.
2. Determine if the system is within the specified lightyear range of at least one of the base systems. Mail is ignored if it's not within range of any system.
3. Filter all attacking ship groups, applying a whitelist of tracked groups. Ignore mail if remainder count is equal to 0.
4. Insight takes the whitelisted attackers from step 3 and applies a blacklist of your allied contacts. Ignore mail if remainder count is equal to 0.
5. Determine attacker flying in the highest valued ship group from the remaining filtered attackers in step 4. This highest attacker and their ship type will make the visual embed.
6. Determine if Insight can mention then match the mention mode of the highest attacking ship group from step 5 with radar settings.
7. Enqueue visual mail for posting.

# Preconfigured Feeds
Preconfigured feeds are derived from base feeds and offer a custom spin on features/settings. Preconfigured feeds require no initial option setup and are mostly static/unchangeable. New preconfigured are added all the time!
## Super losses
* Derived from: Entity feed
* This feed exclusively displays titan or supercarrier losses.
* Available configuration modifications: None
## Abyssal losses
* Derived from: Entity feed
* This feed displays all losses occurring in Abyssal space.
* Available configuration modifications: None
## Excavator losses 
* Derived from: Entity feed
* This feed displays all excavator mining drone losses.
* Available configuration modifications: None
## Freighter Ganks
* Derived from: Entity feed
* This feed displays all freighters and jump freighters destroyed in high-security space.
* Available configuration modifications: None
## Alliance Tournament system stream 
* Derived from: Entity feed
* This feed displays all losses occurring in the region UUA-F4 for the alliance tournament.
* Available configuration modifications: None
## Officer Hunter
* Derived from: Capital radar
* This feed displays universal officer activity when an npc officer is involved in a killmail.
* Available configuration modifications: None
## Universal supers
* Derived from: Capital radar
* Displays universal supercarrier/titan activity regardless of system or standings.
* Available configuration modifications: None
## Alliance Tournament Ship Radar
* Derived from: Capital radar
* Displays universal alliance tournament ship activity regardless of system.
* Available configuration modifications: Synchronized standings through the ```!sync``` command.