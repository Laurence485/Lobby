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
from functools import partial
from random import randint
from typing import Callable

config = get_config()

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
window_wall_width = Window.WALL_WIDTH.value
grid_spacing = config['GRID_SPACING']

player_width = Player_.WIDTH.value
player_height = Player_.HEIGHT.value
player_vel = config['PLAYER_VELOCITY']

bike_sound = config['BIKE_SOUND']
mushroom_sound = config['MUSHROOM_SOUND']


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
        self.width = player_width
        self.height = player_height
        self.vel = player_vel
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
        self.bike_sound = sound(bike_sound)

    def _setup_mushroom_attributes(self) -> None:
        self.start_mushroom_ticks = 0
        self.mushroom = False
        self.mushroom_sound = sound(mushroom_sound)

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
        _animate method.
        """
        if self.walk_count + 1 > 4:
            self.walk_count = 0

        return self.walk_count

    def draw(self, win: Sprite, dt: float) -> None:
        """Draw player onto the screen according to the player's
            direction.
        """
        if self.standing:
            if self.right:
                self._assign_player_animation(
                    dt, self.bike_stand_right_img, self.stand_right_img, win, True
                )
            elif self.left:
                self._assign_player_animation(
                    dt, self.bike_stand_left_img, self.stand_left_img, win, True
                )
            elif self.up:
                self._assign_player_animation(
                    dt, self.bike_stand_up_img, self.stand_up_img, win, True
                )
            elif self.down:
                self._assign_player_animation(
                    dt, self.bike_stand_down_img, self.stand_down_img, win, True
                )
        else:
            if self.right:
                self._assign_player_animation(
                    dt, self.bike_right_imgs, self.walk_right_imgs, win
                )
            elif self.left:
                self._assign_player_animation(
                    dt, self.bike_left_imgs, self.walk_left_imgs, win
                )
            elif self.up:
                self._assign_player_animation(
                    dt, self.bike_up_imgs, self.walk_up_imgs, win
                )
            elif self.down:
                self._assign_player_animation(
                    dt, self.bike_down_imgs, self.walk_down_imgs, win
                )

    def _assign_player_animation(
        self,
        dt: float,
        bike_imgs: Union[List[Sprite], Sprite],
        walk_imgs: Union[List[Sprite], Sprite],
        win: Sprite,
        standing: bool = False,
    ) -> None:

        if self.bike:
            self._animate(bike_imgs, win)
        else:
            self._animate(walk_imgs, win)

        # Cycle through to the next player sprite.
        if not standing:
            self.walk_count += (1 * dt)

    def _animate(
        self,
        player_imgs: Union[List[Sprite], Sprite],
        win: Sprite
    ) -> None:

        try:
            player_img_to_draw = player_imgs[int(self.walk_count // 2)]
        except TypeError:
            player_img_to_draw = player_imgs

        if self.in_slow_area:
            self._draw_player_top_half_only(win, player_img_to_draw)
        else:
            self._draw_player(win, player_img_to_draw)

    def _draw_player_top_half_only(
        self,
        win: Sprite,
        player_img: Sprite
    ) -> None:

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
            self.vel = player_vel - reduced_speed

        else:
            self.vel = player_vel
            # We must re-sync with the grid as the player position is no
            # longer to the nearest square.
            # self._sync_player_pos()

    def move(self, dt) -> None:
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
                print(dt)

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
            print('Debug: Frozen on a wall. Reassigning (x,y) position.')
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
        if self.x > window_height - window_wall_width - grid_spacing:
            self.x -= self.vel * dt
        elif self.x < 0:
            self.x += self.vel * dt
        elif self.y < 0:
            self.y += self.vel * dt
        elif self.y > window_height - self.height:
            self.y -= self.vel * dt

    def _sync_player_pos(self) -> None:
        """Sync player x,y with grid."""
        self.x, self.y = (
            sync_value_with_grid(self.x), sync_value_with_grid(self.y)
        )
