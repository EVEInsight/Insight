Insight utilizes various colors to provide state information.

# Table of contents
- [Bot Status](#bot-status)
  * [Format](#format)
  * [Status colors](#status-colors)
- [Embedded visual left sidebar](#embedded-visual-left-sidebar)
  * [Entity Feeds](#entity-feeds)
  * [Capital radar feeds](#capital-radar-feeds)

# Bot Status
![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/botstatus.png)
## Format 
```Watching CPU:{1}% MEM:{2}% v{3} [Stats 5m][zK] Add:{4}, Delay: {5}({6}), Next: {7} [Insight] Sent: {8}, Delay: {9}```
1. System CPU usage at time of status update
2. System memory usage at time of status update
3. Version string. If a new release is available from Github, elements 1-3 will be replaced with an ```Update available``` text notification.
4. Number of killmails fetched from zkillboard in the last 5 minutes.
5. Median delay from (Insight RedisQ receive datetime) - (killmail datetime occurrence).
6. Average time to resolve missing names to IDs and reload the sqlalchemy object in memory.
7. Average time between response code 200s from RedisQ.
8. Number of embedded visual messages sent to all feed services in the last 5 minutes.
9. Average delay for a killmail to be sent through feed filter and successfully post to Discord api.
## Status colors
| Color| Status |
|---|---|
| Green | All Insight services are running without significant delays.|
| Yellow | Significant zKillboard/RedisQ delays or errors.|
| Red  | Significant delays posting messages to Discord api. This status can be caused by Discord api outages or Insight hitting the Discord message rate limit.|

# Embedded visual left sidebar
## Entity Feeds
| Color| Mail type|
|---|---|
| ![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/entity_k.png)| Killmail. Tracked entity participated in a killmail.|
| ![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/entity_l.png) | Lossmail. Tracked entity was the killmail.|

## Capital radar feeds
| Color| Occurrence delay |
|---|---|
| ![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/radar_recent.png)| Under 1 minute ago |
| ![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/radar_mid.png) | 1-5 minutes ago |
| ![](https://raw.githubusercontent.com/Nathan-LS/Insight/dev/docs/images/radar_old.png) | 5+ minutes ago |
