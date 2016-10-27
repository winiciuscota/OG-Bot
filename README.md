#Ogame-bot

This bot is intended to provide automation for simple tasks in Ogame. At this point the bot should be able to work in all servers.
At the beginning the bot could only build defenses, now it can do a variety of tasks<br />

#Usage:

1 - Install the requirements: <br />
pip install -r requirements.txt <br />

2 - Modify the user-sample.cfg file and rename it to user.cfg <br />

3 - The program also accepts two arguments. the first will override the DefaultMode and the second will override DefaultOriginPlanet <br />

The currently supported modes are: <br />
- overview - logs overview data <br />
- explore - send expeditions and attack nearby inactive players <br />
- attack_inactive_planets - attack nearby inactive players <br />
- auto_build_defenses - build defenses <br />
- auto_build_defenses_to_planet - build defenses to planet x(must be one of your planets) <br />
- transport_resources_to_planet - transport resources from all of your planets to planet x(must be one of your planets) <br />
- transport_resources_to_weaker_planet - transport resources from all of your planets to the planet that has less buldings <br />
- auto_build_structure_to_weaker_planet - Build structure on the weaker planet
- auto_build_structures - Build structures on planets
- auto_research - Research on your homeplanet

e.g.: <br />

python main.py -m explore - will run the bot on the explorer mode (send expeditions and attack inactive targets) <br />

python main.py -m transport_resources_to_planet planet_name - will transport all resources to the planet_name planet (must be one of your planets) <br />


4 - Have a nice day while the bot takes care of the boring parts =]<br />

#Features:

- Spend Resources on defenses<br />
- Transport resources from all of your planets into one of your planets<br />
- Auto spy inactive players nearby<br />
- Auto attack inactive players nearby<br />
- Send Expeditons<br />
- Overview player info<br />
- Build structures<br />
- Research Technologies <br />

#Credits:

Many thanks to Rafał Furmański(http://rafal-furmanski.com/) for letting me use some snippets of his code (https://github.com/r4fek/ogame-bot).<br />
Rafał Furmański's work was crucial for creating the functions to build defenses, send fleets and fetch galaxy's data <br/>
