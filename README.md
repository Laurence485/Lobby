# Pokéwars

Description:

Pokéwars is a realtime online multiplayer game made using sprites from Pokemon Leaf Green and Fire Red. 

This project was made using python3.7, pygame and the sockets module to handle incoming connections.

The player must navigate randomly generated maps, gathering weapons and power-ups from long grass and deep pools, and destroy enemy players.

The game supports 7 native maps, each using a range of difference sprites and terrains from Pokémon. 

The Map class in  map_generation.py has generate_map(),save() and load() functions, which can be used to generate new maps by passing in a list of sprites as well as to save and load maps. 

The game maps used can be changed by editing maps[] in config.py. Any newly generated maps should be added here.


# Further Game Details

On connection player must enter name, and is then assigned a colour based on their assigned connection ID.

Players can find new weapons and power ups (currently 'bike' and 'mushroom' only) by searching in grass and water.

Navigating through grass and water reduces the players movement speed. 

Bikes 2x the players speed.

Mushrooms 2x the players size - providing temporary immunity to death and the ability to trample other players via contact.

Game statistics are shown in the menu/leaderboard (Z).

Host is considered to be first person connected to the server.

# Controls

Movement: Arrow Keys

Shoot: Spacebar

Strafe: S

Menu/Leaderboard: Z

Show Grid: X

Change Map (Host only): C

# Requirements
- python3.7

- pygame

# How to run

Change HOST and PORT in config.py to reflect your setup.

Ideally place server.py and config.py on a server. Multiple instances can then be launched from anywhere with many players playing simultaneously.

Another option is to download and use Hamachi to simulate your LAN. 

Only the host player must run server.py. Other players need only run game.py.

# LICENSE

<em>Not for commercial use</em>. Please credit me if you intend to use code from this game.

# Screenshots


![ss1](https://user-images.githubusercontent.com/31314787/75720569-ad602880-5cce-11ea-9d93-b7b177b4cfec.PNG)
![ss2](https://user-images.githubusercontent.com/31314787/75720244-0f6c5e00-5cce-11ea-8e1a-943334dad200.PNG)
![ss3](https://user-images.githubusercontent.com/31314787/75720246-1004f480-5cce-11ea-91be-46d8b6434351.PNG)
