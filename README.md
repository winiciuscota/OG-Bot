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

run the program with username, password, server, mode and target planet as arguments(the last parameter is only required if the selected mode operates over a target planet).

ie: python main.py username password universe mode planetname

Alternatively you can create a user.cfg file on the project directory. Program arguments will have precedence.

the user.cfg file should look like this:

[UserInfo] <br />
username = your_username <br />
password = your_password <br />
universe = your_universe <br />

[Settings] <br />
Mode = transport_resources_to_planet <br />
TargetPlanet = target_planet <br />

#The currently supported modes are:
auto_build_defenses: Spend all resouces on defenses for all planets
get_defenses: Display defenses for all planets
get_ships: Display all ships that are not in missions for all planets
get_planets: Display all your planets
transport_resources_to_planet: transport all resources of your planets to the target planet (from the config file)
