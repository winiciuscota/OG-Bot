#Ogame-bot

This bot is intended to provide automation for simple tasks in Ogame. At the moment the bot only works on the brazilian server and the only useful thing it can do is to spend all resources on defenses.

In the future I intend to have the following features:

Spend all resources on defenses. -Done<br />
Auto build structures. - Done<br />
Auto attack inactive players. - Done<br />
Fleet save.<br />
Alert when being atacked(through email).<br />

I'm new to python, I'm using it because I believe is the best language for this kind of job, I also want to learn more about it. Any criticism is very much appreciated.

#Instructions on how to use:

Modify the user.cfg file on the project directory.

the user.cfg file should look like this:

[UserInfo]
Username = ishak <br />
Password = 15172114 <br />
Universe = 114 <br />
	
[Settings]
DefaultMode = auto_attack_inactive_planets <br />
DefaultOriginPlanet = antey <br />
#how much systems away the bot should be able to attack <br />
AttackRange = 15  <br />
#wait 60 seconds for probes to return <br />
HowLongToWaitForProbes = 90  <br />

The program also accepts two arguments. the first will override the DefaultMode
 and the second will override DefaultOriginPlanet

The currently supported modes are: <br />
    log_defenses <br /> 
    log_ships <br />
    log_planets <br />
    overview <br />
    auto_build_defenses <br />
    auto_build_structures <br />
    auto_build_structure_to_planet <br />
    auto_build_defenses_to_planet <br />
    transport_resources_to_planet <br />
    log_planets_in_same_system <br />
    log_nearest_planets <br />
    log_nearest_inactive_planets <br />
    spy_nearest_planets <br />
    spy_nearest_inactive_planets <br />
    log_spy_reports <br />
    attack_inactive_planets_from_spy_reports <br />
    log_index_page <br />
    log_game_datetime <br />
    auto_attack_inactive_planets <br />
    log_fleet_movement <br />
    auto_spy_inactive_planets <br />
    clear_inbox <br />
    
#Credits:

Many thanks to Rafał Furmański(http://rafal-furmanski.com/) for letting me use some snippets of his code (https://github.com/r4fek/ogame-bot).<br />
Rafał Furmański's work was crucial for creating the functions to build defenses, send fleets and fetch galaxy's data <br/>


