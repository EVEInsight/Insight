# The Future of Insight
Greetings! I am Natuli, the creator of the [Insight Discord bot project](https://github.com/EVEInsight/Insight) and operator of the public [Insight Discord bot instance](https://discord.eveinsight.net/).
Insight streamed kills to Discord from zKillboard.com to provide corporate/alliance feeds, capital/supercapital radar, ship proximity detection, and more for nearly four years.

I have maintained Insight as a project for four years and during the journey I have learned quite a bit about the EVE API, asynchronous programming, the Discord API, microservices, hosting infrastructure, and testing/deployment automation.
A good amount of time (and money) has gone in to maintaining this project and hosting it freely for anyone to use and enjoy.

Over the years I have struggled with motivation to add features, improve issues, and rewrite broken code for Insight and the project has been in a pseudo maintenance mode for some time now.
I believe it's now time to officially move on.

I am sad to announce that I will no longer be maintaining and supporting the Insight open-source project on GitHub as of today.
I will be decommissioning the public Insight Discord bot on May 13th, 2022 at 04:00 AM UTC.
The [GitHub repo](https://github.com/EVEInsight/Insight) will remain open so anyone can freely fork and work on the project. The [Docker Hub](https://hub.docker.com/r/nathanls/insight) repository will remain up along with the recently updated setup guide if you want to pull and host a Discord bot instance. 

I truly appreciate the EVE community and am grateful for the motivation I received to build this project. You all are awesome people and I wish you the best!

I have an [FAQ](#FAQ) section detailing my reasoning and what happens next.


# Project Backstory
Back in 2018 I wanted to build a tool that would alert of nearby capitals and shiny ships in jump range given a system and provide notifications if there was detected activity.
Everyone was on Discord and there were solid wrapper libraries around the Discord API to build an asynchronous app to parse kills from the zKillboard.com API, enrich the data, and publish mails to Discord.

The goal was to build a tool that could enhance the EVE experience by bringing EVE directly to Discord communities whether that be through showing off the latest activity or preparing insights into the fleet composition of nearby hostiles near your home systems to engage.
I wanted to build a simple bot that could easily be configured through Discord rather than being configured through config files on the back-end / host. 
It was also important that the project be open-source and freely available to host yourself and to make modifications so the Insight project on GitHub was created.

The initial deployment was a mess, relied on long SQL queries, and was unoptimized for Python Asynchronous architecture.
The project was completely rewritten in Spring 2018 and the public Insight bot still running today was deployed in July 2018.
The current code is still messy and taped together, but I am proud it has held up and still functions. There was a time when reacting to a message completely crashed the entire service which led to a few days of fun and frantic debugging!

Since July 2018 there have been improvements including the switch to Docker / microservices, additional post visuals, addition of PostgreSQL support, more feed types, and utility commands (local scan, etc).

The current public Discord bot instance has over 4,200 active feeds streaming kills to Discord channels and is a member of over 2,000 Discord communities. During busy activity periods the number of successfully delivered messages to channels could reach 25,000+ per hour. 
The database contains a historical 21 million killmail and 100 million attacker rows parsed since July 2018 and is nearly 30GB in size!

A second rewrite was in the works through the [InsightCore](https://github.com/EVEInsight/InsightCore) project in response to the 2022 [Discord API Message Content Privileged Intent](https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-FAQ) changes and technical debt of the current code. 
InsightCore was pretty cool and built around the Celery library using RabbitMQ to distribute tasks across multiple stateless containers where every attribute of mails could be filtered through a JSON configuration document. 
The InsightCore project was designed to have streams configured through a web API and support multiple target platforms (including Slack) through webhooks to remove the reliance on a chat/Discord bot for posting messages.

# FAQ
I imagine there will be some questions about what happens next.

## Why are you stopping Insight development?
Stopping Insight development has been on my mind for a while and is not a sudden decision I take lightly.
Deciding to stop development and hosting of Insight is a decision not made in anger but one made in disappointment.

I would summarize my reasoning to be a combination of three primary factors:
* The previous and current lack of direction / vision CCP has for EVE
* Discord API changes through the new [Message Content Privileged Intent](https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-FAQ) and the resulting changes required to operate the public Insight bot
* Lack of time and motivation for maintaining, testing, and debugging new features/improvements when a rewrite is necessary

In the past, Insight and other Discord bot projects would parse text messages for command indicators (!, /, ?, etc.) as there was no other functionality built into the Discord API to trigger a command.
Discord is pushing for the adoption of their Interactions API (slash commands, buttons, menus, etc.) while many third party Discord API wrapper library developers were stressed to rewrite their libraries to suddenly support these new features.

In April 2022 (now delayed to August 2022) all verified bots in over 75 servers would need to switch over to support the new Interactions API or lose access to the old way of parsing for commands through reading channel text messages. 
The intent isn't provided if you only want to maintain the old way of reading command triggers through text messages.
I understand Discord's reasoning to use messages intent and applaud them for taking steps to improve user privacy and design more interactive features.

However, supporting the new Discord changes and requirements would require a significant amount of work on Insight. 
Insight needed refactoring, and it was extremely difficult to make changes or build new features into the limiting architecture Insight was designed with.


Instead of writing code for Insight I decided to start work on the [InsightCore](https://github.com/EVEInsight/InsightCore) project to function as a replacement and complete rewrite that would be easier to maintain and collaborate on in place of Insight / this repo.
InsightCore would directly publish to a channel through webhooks and support far superior stream customization through a web API instead of Discord command menus. 
There would be no bot and Discord wouldn't be the only possible destination as the project was not designed around Discord like Insight was.

The goal was to have InsightCore completed by the message intent cutoff but the recent changes in EVE have me concerned over the game's future and have killed off any remaining motivation I had left for developing EVE tools.

## Why can't you continue hosting Insight until August 2022?
Cost and I don't want to commit to continued support for additional months seeing as I have stopped further development and maintenance as of today.

Some of my EVE subscriptions have ended and a few more are ending in the coming weeks. It's time to finally move on.

## Can I host your stuff?
No. The database and data for the public Insight Discord bot containing all feed configurations and user ESI data will not be available or passed to another operator/host.
I will not be taking applications and will not consider providing the backend database to anyone.

You are free to host an instance of Insight with a new fresh blank database.

## Can I have your stuff?
No. Maybe things will get better in the future and I decide to come back. Who knows?

## What happens to the Insight public bot on May 13th?
The public Discord bot that is a member of 2,000 servers and streams to over 4,200 feeds will shut down and be deleted.
The third-party EVE / ESI application used for accessing pilot contact information will also be deleted. 

## What happens to EVEInsight.net and the websites?
I don't intend on dropping registration on the EVEInsight.net domain for the foreseeable future. 
The landing website will be shut down with the public bot and the wiki will be shut down some time after the bot.

## What happens to the Git repo? Can I take over the repo?
The Git repo will eventually be archived (set read-only) and will not pass to another maintainer. You are free to fork and make changes from your new repo that you maintain.

## What happens to the support Discord server?
The support Discord server will be closed and deleted sometime in the future.

## How do I host Insight myself?
The easiest method is through Docker but keep in mind this project is no longer maintained or supported so proceed at your own risk.
The [Docker Hub repo](https://hub.docker.com/r/nathanls/insight) has instructions and a guide to get you started.

## I want Insight to keep working!
Your option is to either fork the project and maintain it or host Insight through a Docker container.
Just a warning though that the code has lots of technical debt and is quite messy if you decide on code development.

I strongly suggest forking the [InsightCore](https://github.com/EVEInsight/InsightCore) repo and continuing off of that code instead of Insight/this repo.

## I want to maintain or continue developing Insight!
I strongly suggest starting your development with the unfinished [InsightCore](https://github.com/EVEInsight/InsightCore) project instead of [Insight](https://github.com/EVEInsight/Insight).
Insight / this repo has years of technical debt, undocumented code, and is unnecessarily difficult to understand. InsightCore is well documented, organized, and easy to understand despite being unfinished.

I was building the InsightCore project as a complete rewrite due to my own issues and difficulties maintaining and developing new features for Insight.
InsightCore provides an excellent framework to build on.

## Would you consider development of this project some time in the future?
On Insight, no. If I were to develop a similar tool for EVE all development focus would be on the rewrite (InsightCore).

## Will you be working on InsightCore in place of Insight?
No, development for InsightCore has ceased for now as well. If I return I would develop InsightCore / rewrite instead of maintaining Insight / this repo.

## Are you quitting EVE?
For the foreseeable future, yes. All of my accounts are unsubbed and will run out over the next few days/weeks.
CCP might turn things around in the future, but I currently lack confidence in CCP making meaningful changes after years of underwhelming updates.

# Acknowledgments
I would like to thank the following people, communities, and tool maintainers for either designing resources used by Insight or providing support:
* Danny, the discord.py maintainers, and community - Thank you for building the core library that Insight was built around and providing answers to my questions.
* Squizz and zKillboard.com - Insight simply wouldn't exist without zKill. Thank you for making your data available through APIs.
* Steve and Fuzzwork.co.uk - Your work of combining the SDE into a simple and easy to use database made importing static EVE data into Insight simple.
* The maintainers of the following libraries which made development of Insight so much easier:
  * [SQLAlchemy](https://www.sqlalchemy.org/) 
  * [NetworkX](https://github.com/networkx/networkx) 
  * [AIOHTTP](https://aiohttp.readthedocs.io/en/stable/)
  * [janus](https://github.com/aio-libs/janus) 
  * [Pympler](https://github.com/pympler/pympler) 
  * [cryptography](https://cryptography.io/en/latest/) 
  * [swagger-client](https://github.com/swagger-api/swagger-codegen)

# Signing Off
Thank you for enjoying Insight and being a part of the journey! The EVE community is truly awesome.

Fly safe o7
