# Insight
# Insight v1.3.1
Insight provides EVE Online killmail streaming for Discord. Insight can stream personal or corporate killboards, detect supercapitals with a proximity radar, and more!
Killmails and intel are presented in Discord rich embeds containing relevant links and images to quickly identify important information.

[Invite Insight](#links) to your Discord server and run ```!create``` to begin setting up a feed!

# Links
[![Discord Bots](https://discordbots.org/api/widget/463952393206497290.svg)](https://discordbots.org/bot/463952393206497290)
* **Insight** (with preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=149504&scope=bot)
* **Insight** (without preconfigured role): [Insight Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=463952393206497290&permissions=0&scope=bot)

Insight is available publicly hosted for invites directly to Discord servers.

If you have questions, suggestions, or bug reports feel free to drop by the [project support server.](https://discord.gg/Np3FCUn)
## Running
1. Create and navigate to a directory where you wish to store Insight configuration, logs, and database.
2. Pull and run the image. This command will pull the stable Docker Insight image and initialize the config files in your current directory.

    ```docker run -it --rm -v ${PWD}:/app nathanls/insight --docker-init```
3. Edit ```default-config.ini``` and populate your configuration values in accordance with the Installation.md file. Rename this file to ```config.ini```.
4. Keep the image up to date by checking for updates and then starting Insight: 

    ```docker pull nathanls/insight && docker run -it --rm -v ${PWD}:/app nathanls/insight```