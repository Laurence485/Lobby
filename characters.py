import pygame
import yaml
from utils import load_player_img, random_xy, sound, sync_value_with_grid

with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file)

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
window_wall_width = config['WINDOW_WALL_WIDTH']
player_width = config['PLAYER_WIDTH']
player_height = config['PLAYER_HEIGHT']
grid_spacing = config['GRID_SPACING']
player_vel = config['PLAYER_VELOCITY']
bike_vel = player_vel * config['BIKE_VELOCITY_FACTOR']
bike_sound = config['BIKE_SOUND']
mushroom_sound = config['MUSHROOM_SOUND']


class Player:
    """Create a new player object."""

    def __init__(
        self,
        xy=(50, 70),
        player_id=0,
        username='Noob',
        width=15,
        height=19
    ):
        self.x, self. y = xy
        self.id = player_id
        self.username = username
        self.width = player_width
        self.height = player_height
        self._vel = player_vel  # Non-changing reference.
        self.vel = player_vel
        self.walk_count = 0
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.hit_wall = False
        self.hit_slow = False  # Slow the players movement in grass/water.
        self.left = False
        self.right = False
        self.up = False
        self.down = True
        self.standing = True
        self.strafe = False
        self.setup_player_sprites()
        self.setup_bike_sprites()
        self.setup_bike_attributes()
        self.setup_mushroom_attributes()

    def setup_player_sprites(self) -> None:
        self.stand_left = load_player_img('left1')
        self.stand_right = load_player_img('right1')
        self.stand_up = load_player_img('up1')
        self.stand_down = load_player_img('down1')

        self.walk_left = [load_player_img('left2'), load_player_img('left3')]
        self.walk_right = [
            load_player_img('right2'), load_player_img('right3')
        ]
        self.walk_up = [load_player_img('up2'), load_player_img('up3')]
        self.walk_down = [load_player_img('down2'), load_player_img('down3')]

    def setup_bike_sprites(self) -> None:
        self.stand_left_bike = load_player_img('bike_left1')
        self.stand_right_bike = load_player_img('bike_right1')
        self.stand_up_bike = load_player_img('bike_up1')

        self.bike_left = [
            load_player_img('bike_left2'), load_player_img('bike_left3')
        ]
        self.bike_right = [
            load_player_img('bike_right2'), load_player_img('bike_right3')
        ]
        self.bike_up = [
            load_player_img('bike_up2'), load_player_img('bike_up3')
        ]
        self.bike_down = [
            load_player_img('bike_down2'), load_player_img('bike_down3')
        ]
        self.stand_down_bike = load_player_img('bike_down1')

    def setup_bike_attributes(self) -> None:
        self.bike = False
        self.bike_vel = bike_vel
        self.bike_sound = sound(bike_sound)

    def setup_mushroom_attributes(self) -> None:
        self.start_mushroom_ticks = 0
        self.mushroom = False
        self.mushroom_sound = sound(mushroom_sound)

    def attributes(self) -> dict:
        """Send these attributes from the server to the client for
            multiplayer.
        """
        attrs = {
            'x': self.x,
            'y': self.y,
            'L': self.left,
            'R': self.right,
            'U': self.up,
            'D': self.down,
            'standing': self.standing,
            'walk count': self.walk_count,
            'hit slow': self.hit_slow,
            'bike': self.bike,
            'mushroom': self.mushroom,
            'ID': self.id,
            'username': self.username,
            'map': self.map
        }
        return attrs

    def draw(self, win: pygame.Surface) -> None:
        """Draw player onto the screen according to the player's
            direction.
        """
        if self.walk_count + 1 > 4:
            self.walk_count = 0
        if not self.standing:
            if self.right:
                if self.bike:
                    self.walk_animation(self.bike_right, win)
                else: self.walk_animation(self.walk_right, win)
            elif self.left:
                if self.bike:
                    self.walk_animation(self.bike_left, win)
                else: self.walk_animation(self.walk_left, win)
            elif self.up:
                if self.bike:
                    self.walk_animation(self.bike_up, win)
                else: self.walk_animation(self.walk_up, win)
            elif self.down:
                if self.bike:
                    self.walk_animation(self.bike_down, win)
                else: self.walk_animation(self.walk_down, win)
        else:
            if self.right:
                if self.bike:
                    self.stand_sprite(self.stand_right_bike,win)
                else: self.stand_sprite(self.stand_right,win)
            elif self.left:
                if self.bike:
                    self.stand_sprite(self.stand_left_bike,win)
                else: self.stand_sprite(self.stand_left,win)
            elif self.up:
                if self.bike:
                    self.stand_sprite(self.stand_up_bike,win)
                else: self.stand_sprite(self.stand_up,win)
            elif self.down:
                if self.bike:
                    self.stand_sprite(self.stand_down_bike,win)
                else: self.stand_sprite(self.stand_down,win)

    def walk_animation(self, direction, win):
        if not self.hit_slow:
            if not self.mushroom:
                win.blit(direction[self.walk_count // 2], (self.x, self.y))
            else:
                self.enlarge(direction[self.walk_count // 2], win)
        else: # We are in grass/water.
                win.blit(direction[self.walk_count // 2], (self.x, self.y), (0, 0, sync_value_with_grid(self.width), self.height - self.height // 4))

        self.walk_count += 1

    def stand_sprite(self, direction, win):
        if not self.hit_slow:
            if not self.mushroom:
                win.blit(direction, (self.x,self.y))
            else:
                self.enlarge(direction, win)
        else:
            if not self.mushroom:
                win.blit(direction, (self.x,self.y), (0,0,sync_value_with_grid(self.width),self.height-self.height//4))
            else:
                self.enlarge(direction, win)

    def enlarge(self, direction, win):
        """Scale up the player by 2x"""
        win.blit(pygame.transform.scale2x(direction), (self.x, self.y))

    def check_collisions(
        self,
        collision_nodes: set,
        reduced_speed_nodes: dict
    ) -> None:
        """Check for collisions with immovable objects and with grass
            and water.

        This is a simple collision detection that checks if the player
        coordinates are in the set of object coordinates.
        """
        player_pos = (
            sync_value_with_grid(self.x),
            sync_value_with_grid(self.y + grid_spacing)
        )

        self.hit_wall = True if player_pos in collision_nodes else False
        self.hit_slow = True if player_pos in reduced_speed_nodes else False

        self.assign_player_speed(reduced_speed_nodes, player_pos)

    def assign_player_speed(
        self,
        reduced_speed_nodes: dict,
        player_pos: tuple
    ) -> None:

        if self.hit_slow:
            speed = self._vel if not self.bike else self.bike_vel
            reduced_speed = reduced_speed_nodes[player_pos]
            slow_speed = speed - reduced_speed
            self.vel = slow_speed

        else:
            self.vel = self._vel if not self.bike else self.bike_vel
            # We must re-sync with the grid as the player pos is no
            # longer to the nearest square.
            self.sync_player_pos()

    def move(self) -> None:
        """Move the player with the arrow keys."""
        keys = pygame.key.get_pressed()

        if not self.hit_wall:

            if keys[pygame.K_s]:
                self.strafe = True
            else:
                self.strafe = False
            if keys[pygame.K_LEFT]:
                if self.up and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = True
                    self.down = False
                    self.standing = False
                elif self.down and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = False
                    self.down = True
                    self.standing = False
                else:
                    self.left = True
                    self.right = False
                    self.up = False
                    self.down = False
                    self.standing = False
                self.x -= self.vel
            elif keys[pygame.K_RIGHT]:
                if self.up and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = True
                    self.down = False
                    self.standing = False
                elif self.down and self.strafe:
                    self.left = False
                    self.right = False
                    self.up = False
                    self.down = True
                    self.standing = False
                else:
                    self.left = False
                    self.right = True
                    self.up = False
                    self.down = False
                    self.standing = False
                self.x += self.vel
            elif keys[pygame.K_UP]:
                if self.left and self.strafe:
                    self.left = True
                    self.right = False
                    self.up = False
                    self.down = False
                    self.standing = False
                elif self.right and self.strafe:
                    self.left = False
                    self.right = True
                    self.up = False
                    self.down = False
                    self.standing = False
                else:
                    self.left = False
                    self.right = False
                    self.up = True
                    self.down = False
                    self.standing = False
                self.y -= self.vel
            elif keys[pygame.K_DOWN]:
                if self.left and self.strafe:
                    self.left = True
                    self.right = False
                    self.up = False
                    self.down = False
                    self.standing = False
                elif self.right and self.strafe:
                    self.left = False
                    self.right = True
                    self.up = False
                    self.down = False
                    self.standing = False
                else:
                    self.left = False
                    self.right = False
                    self.up = False
                    self.down = True
                    self.standing = False
                self.y += self.vel
            else:
                self.standing = True
                self.walk_count = 0
        else: #collision
         #self.standing means either:
         #1) we respawned s.t bounds is touching an object, triggering hit_wall = True
         #2) we used mushroom and are not on top of a building
         # --> so find new node...
            if self.standing:
                self.x, self.y = random_xy()
            if self.left: self.x += self.vel
            elif self.right: self.x -= self.vel
            elif self.up: self.y += self.vel
            elif self.down: self.y -= self.vel

        #prevent movement beyond the screen
        #we would normally use self.width but as 10px grid spacing we want to be able to navigate the rightmost square
        if self.x > window_height-window_wall_width-grid_spacing:
            self.x -= self.vel
        elif self.x < 0:
            self.x += self.vel
        elif self.y < 0:
            self.y += self.vel
        elif self.y > window_height-self.height:
            self.y -= self.vel

    def sync_player_pos(self) -> None:
        """sync player x,y with grid"""
        self.x, self.y = (
            sync_value_with_grid(self.x), sync_value_with_grid(self.y)
        )
