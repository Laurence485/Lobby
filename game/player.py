from typing import List, Union

import pygame

from enums.base import Base, Player_, Window
from game.map import Map
from game.typing import Sprite
from game.utils import (
    get_config,
    load_player_img,
    random_xy,
    sound,
    sync_value_with_grid,
    network_data
)
from logger import get_logger
from functools import partial
from random import randint
from typing import Callable

log = get_logger(__name__)
config = get_config()

WINDOW_HEIGHT = config['WINDOW_HEIGHT']
WINDOW_WALL_WIDTH = Window.WALL_WIDTH.value
GRID_SPACING = config['GRID_SPACING']

PLAYER_WIDTH = Player_.WIDTH.value
PLAYER_HEIGHT = Player_.HEIGHT.value
PLAYER_VEL = config['PLAYER_VELOCITY']

BIKE_SOUND = config['BIKE_SOUND']
MUSHROOM_SOUND = config['MUSHROOM_SOUND']


class Player:
    """Create a new player object."""

    def __init__(
        self,
        xy=(50, 70),
        player_id=0,
        username='DefaultUser'
    ):
        self.x, self. y = xy
        self.id = player_id
        self.base_attributes = network_data()
        self.username = username
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel = PLAYER_VEL
        self.walk_count = 0
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.hit_wall = False
        self.in_slow_area = False  # Slow the player's movement in grass/water.
        self.left = False
        self.right = False
        self.up = False
        self.down = True
        self.standing = True
        self.strafe = False
        self._set_player_img_id()
        self._setup_player_sprites()
        self._setup_bike_sprites()
        self._setup_bike_attributes()
        self._setup_mushroom_attributes()
        self._setup_network_attributes()

    @property
    def _current_step(self) -> int:
        return self.animation_loop()

    @property
    def attributes(self) -> dict:
        """Attributes to send to/from the client and server."""
        for attribute in self.base_attributes.keys():
            self.base_attributes[attribute] = getattr(self, attribute)

        return self.base_attributes

    def _set_player_img_id(self) -> int:
        """Set the image id (which will determine the players colour)
        based on the players' id."""
        if self.id < Base.PLAYER_COLOURS.value:
            img_id = self.id
        else:
            img_id = randint(0, Base.PLAYER_COLOURS.value - 1)

        setattr(self, 'img_id', img_id)

    def _load_player_img(self, img: str) -> Callable:
        return partial(
            load_player_img, img_id=getattr(self, 'img_id', 0)
        )(img)

    def _setup_player_sprites(self) -> None:
        self.stand_left_img = self._load_player_img('left1')
        self.stand_right_img = self._load_player_img('right1')
        self.stand_up_img = self._load_player_img('up1')
        self.stand_down_img = self._load_player_img('down1')

        self.walk_left_imgs = [
            self._load_player_img('left2'),
            self._load_player_img('left3')
        ]
        self.walk_right_imgs = [
            self._load_player_img('right2'),
            self._load_player_img('right3')
        ]
        self.walk_up_imgs = [
            self._load_player_img('up2'),
            self._load_player_img('up3')
        ]
        self.walk_down_imgs = [
            self._load_player_img('down2'),
            self._load_player_img('down3')
        ]

    def _setup_bike_sprites(self) -> None:
        self.bike_stand_left_img = self._load_player_img('bike_left1')
        self.bike_stand_right_img = self._load_player_img('bike_right1')
        self.bike_stand_up_img = self._load_player_img('bike_up1')
        self.bike_stand_down_img = self._load_player_img('bike_down1')

        self.bike_left_imgs = [
            self._load_player_img('bike_left2'),
            self._load_player_img('bike_left3')
        ]
        self.bike_right_imgs = [
            self._load_player_img('bike_right2'),
            self._load_player_img('bike_right3')
        ]
        self.bike_up_imgs = [
            self._load_player_img('bike_up2'),
            self._load_player_img('bike_up3')
        ]
        self.bike_down_imgs = [
            self._load_player_img('bike_down2'),
            self._load_player_img('bike_down3')
        ]

    def _setup_bike_attributes(self) -> None:
        self.bike = False
        self.bike_sound = sound(BIKE_SOUND)

    def _setup_mushroom_attributes(self) -> None:
        self.start_mushroom_ticks = 0
        self.mushroom = False
        self.mushroom_sound = sound(MUSHROOM_SOUND)

    def _setup_network_attributes(self) -> None:
        for expected_attr in self.base_attributes.keys():
            try:
                getattr(self, expected_attr)
            except AttributeError as e:
                raise AttributeError(
                    (
                        'Expected base player attributes to send to the'
                        ' network do not match the attributes in the'
                        ' Player class. \n'
                        f'Error: {e}.'
                    )
                )

    def animation_loop(self) -> int:
        """A simple counter to loop through the players' sprites.

        The numbers are important here as each direction has 2 possible
        animations. They help determine not only the speed of the
        animation cycle but also which sprite is selected in the
        _select_img_to_draw method.
        """
        if self.walk_count + 1 > 4:
            self.walk_count = 0

        return self.walk_count

    def animate(self, dt: float) -> None:
        """ Cycle through to the next player sprite."""
        if not self.standing:
            self.walk_count += (1 * dt)

    def draw(self, win: Sprite, dt: float) -> None:
        """Assign direction in which the player will be drawn.
        """
        if self.right:
            self._assign_player_imgs_to_draw(
                dt, win, direction='right'
            )
        elif self.left:
            self._assign_player_imgs_to_draw(
                dt, win, direction='left'
            )
        elif self.up:
            self._assign_player_imgs_to_draw(
                dt, win, direction='up'
            )
        elif self.down:
            self._assign_player_imgs_to_draw(
                dt, win, direction='down'
            )

    def _assign_player_imgs_to_draw(
        self,
        dt: float,
        win: Sprite,
        direction: str,
    ) -> None:
        """Get player images to be drawn according to the player's
            direction and state.
        """
        if self.standing:
            bike_imgs = getattr(self, f'bike_stand_{direction}_img')
            walk_imgs = getattr(self, f'stand_{direction}_img')
        else:
            bike_imgs = getattr(self, f'bike_{direction}_imgs')
            walk_imgs = getattr(self, f'walk_{direction}_imgs')

        if self.bike:
            self._select_img_to_draw(bike_imgs, win)
        else:
            self._select_img_to_draw(walk_imgs, win)

    def _select_img_to_draw(
        self,
        player_imgs: Union[List[Sprite], Sprite],
        win: Sprite
    ) -> None:
        """Select the specific player image to be drawn."""
        try:
            img_to_draw = int(self.walk_count // 2)
            img = player_imgs[img_to_draw]
        except TypeError:
            img = player_imgs

        if self.in_slow_area:
            self._draw_player_top_half_only(win, img)
        else:
            self._draw_player(win, img)

    def _draw_player_top_half_only(
        self,
        win: Sprite,
        player_img: Sprite
    ) -> None:
        """Player is in grass or water."""
        win.blit(
            player_img,
            (self.x, self.y),
            (0, 0, sync_value_with_grid(self.width),
                self.height - self.height // 4)
        )

    def _draw_player(self, win: Sprite, player_img: Sprite) -> None:
        win.blit(player_img, (self.x, self.y))

    def _enlarge(self, player_img: Sprite, win: Sprite) -> None:
        """Scale up the player size by 2."""
        win.blit(pygame.transform.scale2x(player_img), (self.x, self.y))

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
            sync_value_with_grid(self.y + 10)
        )

        self.hit_wall = True if player_pos in collision_nodes else False
        self.in_slow_area = (
            True if player_pos in reduced_speed_nodes else False
        )

        self._assign_player_speed(reduced_speed_nodes, player_pos)

    def _assign_player_speed(
        self,
        reduced_speed_nodes: dict,
        player_pos: tuple
    ) -> None:
        """Assign player speed according to player location."""
        if self.in_slow_area:
            reduced_speed = reduced_speed_nodes[player_pos]
            self.vel = PLAYER_VEL - reduced_speed
        else:
            self.vel = PLAYER_VEL

    def move(self, dt: float) -> None:
        """Move the player with the arrow keys."""
        keys = pygame.key.get_pressed()

        if self.hit_wall:
            self._prevent_movement_into_wall(dt)
        else:
            self.strafe = True if keys[pygame.K_s] else False

            if keys[pygame.K_LEFT]:
                if self.up and self.strafe:
                    self._set_directions("up")
                elif self.down and self.strafe:
                    self._set_directions("down")
                else:
                    self._set_directions("left")
                self.x -= self.vel * dt

            elif keys[pygame.K_RIGHT]:
                if self.up and self.strafe:
                    self._set_directions("up")
                elif self.down and self.strafe:
                    self._set_directions("down")
                else:
                    self._set_directions("right")
                self.x += self.vel * dt

            elif keys[pygame.K_UP]:
                if self.left and self.strafe:
                    self._set_directions("left")
                elif self.right and self.strafe:
                    self._set_directions("right")
                else:
                    self._set_directions("up")
                self.y -= self.vel * dt

            elif keys[pygame.K_DOWN]:
                if self.left and self.strafe:
                    self._set_directions("left")
                elif self.right and self.strafe:
                    self._set_directions("right")
                else:
                    self._set_directions("down")
                self.y += self.vel * dt

            else:
                self.standing = True
                self.walk_count = 0

    def _prevent_movement_into_wall(self, dt) -> None:
        if self.standing:
            log.debug('Frozen on a wall. Reassigning (x,y) position.')
            self.x, self.y = random_xy(Map.nodes)
        if self.left:
            self.x += self.vel * dt
        elif self.right:
            self.x -= self.vel * dt
        elif self.up:
            self.y += self.vel * dt
        elif self.down:
            self.y -= self.vel * dt

    def _set_directions(self, current_direction: str) -> None:
        """Set all directions to false except the current direction in
        which the player is moving.
        """
        setattr(self, current_direction, True)

        other_directions = (
            {'left', 'right', 'up', 'down'} - {current_direction}
        )

        for direction in other_directions:
            setattr(self, direction, False)

        self.standing = False

    def prevent_movement_beyond_screen(self, dt) -> None:
        # We want to be able to navigate the rightmost square.
        if self.x > WINDOW_HEIGHT - WINDOW_WALL_WIDTH - GRID_SPACING:
            self.x -= self.vel * dt
        elif self.x < 0:
            self.x += self.vel * dt
        elif self.y < 0:
            self.y += self.vel * dt
        elif self.y > WINDOW_HEIGHT - self.height:
            self.y -= self.vel * dt
