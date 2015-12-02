#Ogame-bot

This bot is intended to provide automation for simple tasks in Ogame. At the moment the bot only works on the brazilian server and the only useful thing it can do is to spend all resources on defenses.

In the future I intend to have the following features:

Spend all resources on defenses.<br />
Auto build resources.<br />
Auto attack inactive players.<br />
Fleet save.<br />
Alert when being atacked(through email).<br />

I'm new to python, I'm using it because I believe is the best language for this kind of job, I also want to learn more about it. Any criticism is very much appreciated.

#Instructions on how to use:

run the program with username, password and server as arguments.

ie: python main.py username password universe

Alternatively you can create a user.cfg file on the project directory. Program arguments will have precedence.

the user.cfg file should look like this:

[UserInfo] <br />
username = your_username <br />
password = your_password <br />
universe = your_universe <br />
