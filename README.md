# Lobby

Lobby is a Python 3.9 online multiplayer chat game using sprites from Pokémon.

It is a work in progress.

## Getting started

Pip install pipenv if needed

```cd Lobby/``` 

### Host:

Install requirements - ```pipenv install```

Start the redis database - ```make redis``` (requires Docker).

Start python virtual env - ```pipenv shell``` 

Set HOST and PORT environment variables for the corresponding host address and port for connection.

Start the server - ```python start_server.py```



### Clients:

Install requirements - ```pipenv install```

Start python virtual env - ```pipenv shell``` 

Set HOST and PORT environment variables for the corresponding host address and port for connection.

Start the game - ```python main.py```


### Controls:

Press Enter to type.

Use Arrow Keys to move.

Press X to show the grid.

Press B to use the bike.

To generate new maps see ```pythom main.py --help```
