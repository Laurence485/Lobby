#-------window and grid---------
window_width = 400
window_height = 400
window_wall_width = 70 #this is the rock wall on the right of some maps
grid_spacing = 10 #square size for grid

#--------player attributes-----------
player_vel = grid_spacing
bike_vel = player_vel

#----------mutliplayer-------------
HOST = "localhost"
PORT = 12345
buffer_size = 2048
num_players = 5
maps = ['myfirstmap','grass','water','trees','city', 'oasis','empty']

#---------weapons---------------
bikes = 5
mushrooms = 2

#------------sounds--------------
theme = 'sounds/sevii_islands.mp3'
kill_sound = 'sounds/kill.wav'
bike_sound = 'sounds/bike.wav'
bike_active_sound = 'sounds/Bike - raining blood.mp3'
death_sound = 'sounds/death.wav'
mushroom_sound = 'sounds/mushroom.wav'
mushroom_active_sound = 'sounds/mushroom - south of heaven.mp3'
pokeball_sound = 'sounds/pokeball.wav'
trample_sound = 'sounds/trample.wav'