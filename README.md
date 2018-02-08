<p align="center"><img
    width="350"
    src="https://i.imgur.com/3w0T9b5.png"
></p>
<h1 align="center">TWOWBot</h1>

A simple bot for hosting miniTWOWs on [Discord](https://discordapp.com). **You can add the bot to your
server using [this link.](https://htcraft.ml/twowbot)** Or, if you would like to help test experimental
features, you can invite the beta/unstable bot using [this link.](https://htcraft.ml/twowbeta)

![Python3.6](https://img.shields.io/badge/python-3.6-blue.svg)
![Discord.py rewrite](https://img.shields.io/badge/discord.py-rewrite-orange.svg)
[![Discord Server](https://discordapp.com/api/guilds/303616392710586373/widget.png)](https://discord.gg/t58ukQW)

### About TWOWBot
#### This bot is being developed by:
* [Bottersnike#3605](https://github.com/Bottersnike)
* [hanss314#0128](https://github.com/hanss314)
* [Noahkiq#0493](https://github.com/Noahkiq)
#### The bots are being hosted by:
* [hanss314#0128](https://github.com/hanss314)

---
### How to use TWOWBot:
#### Hosting an mTWOW:
The host of an mTWOW has a couple of commands for them to use:
* **`set_prompt`** will set the prompt for the round.
* **`responses`** will send you a DM listing all of the responses so far.
* **`start_voting`** will then close responses and allow people to vote.
* Finally, **`results`** will end the round and show results
* You can also use **`transfer`** to make someone else the host of the mTWOW.
#### Traditional mTWOWs:
The owner of a mTWOW can setup a traditional mTWOW where anyone can host:
* **`can_queue on`** will allow people to join the hosting queue with **`join_queue`**.
* **`queue_timer`** will allow you to set a timer for the events.
* Use **`help queue_timer`** for help.
* **`skip_host`** will skip the current host and start a fresh season.
#### Participating in an mTWOW:
When you are participating, you also have some commands you can use:
* **`respond`**, when in a DM, allows you to respond to a prompt.
* **`vote`**, when in a DM, will first generate your voting slide, and then
allow you to vote on it.
#### Other useful commands:
There are a few commands that are useful to know:
* **`prompt`** will show you the current prompt.
* **`round`** and **`season`** will tell you the round and season number
respectively.
* **`id`** will get you the channel identifier for that mTWOW. This is needed
when responding or voting.
#### Getting help:
All of these commands, and more, are available in the **`help`** command.
If you want to invite the bot to your server, or join the official one, use **`about`**.
If you are interested in hosting this bot for yourself, check the GitHub linked in the **`about`** command,
or DM one of the developers (also in the **`about`** command).

---
### All commands:
| command        | brief description |
| -------------- | ----------------- |
| `round`        | Get the current round number. |
| `sudo`         | Run a command ignoring every check. |
| `evaluate`     | Run some code. |
| `vote`         | Vote on the responses. |
| `die`          | Disconnects the bot. |
| `respond`      | Respond to the current prompt. |
| `say`          | Get te bot to say something. |
| `help`         | This help message :D |
| `ping`         | Ping the bot. |
| `id`           | Get the server ID used in voting. |
| `role_ids`     | Get all of the role ids for the server. |
| `about`        | Get info about the bot. |
| `me`           | Get info about yourself. |
| `prompt`       | Get the current prompt. |
| `how`          | Get instructions on hosting a mTWOW. |
| `season`       | Get the current season number. |
| `register`     | Setup channel initially. |
| `show_config`  | Sends the config file for this channel. |
| `set_times`    | Set timer for next events.  Events are voting and results. |
| `set_prompt`   | Set the prompt for this round. |
| `start_voting` | Start voting. |
| `transfer`     | Transfer ownership of this mTWOW. |
| `results`      | End this round and show results. |
| `delete`       | Delete the mTWOW. |
| `responses`    | List all responses this round. |

To get indepth help into any of these commands including what arguments they
require and who can use them, use the `help` command.

### How to host the bot:
Hosting TWOWBot is relatively simple. To download it run the following commands:
```sh
$ git clone https://github.com/HTSTEM/TWOW_Bot TWOWBot
$ cd TWOWBot/
$ git checkout yaml
```
*Replace `yaml` in the above command with `stable` if you want to run versions
that are usually stable.* From there, there is a handy setup script to get you
on your feet:
```sh
$ python3 setup.py
```
You will then need to edit `src/config.yml` with your information. Your bot
token can be found [here](https://discordapp.com/developers/applications/me),
the `developers` section should have your ID in it, and then anyone else that
might need full control of the bot,for example, any alt accounts you have. The
`host` should have your ID in it.

Once you've configured the bot, you can start it using:
```
run.cmd
```
Don't worry about being on Linux or Windows, the script will automatically
detect which one you are using and then run the correct startup script for
you.

This script will expect you to be running python 3.6. It will check for
`python3` and `python` as commands in that order, and use the first one it
finds. It will also start it in a loop, so if the bot crashes, it will start
back up. If you want to only run it once, use:
```sh
$ cd src/
$ python3 bot.py
```
