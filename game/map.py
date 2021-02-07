import pickle
from random import seed

from config.sprites import config as get_sprites_config_dict
from enums.base import Window
from game.typing import Sprite
from game.utils import get_config, random_xy, sync_value_with_grid
from typing import Set

base_config = get_config()

WINDOW_WIDTH = base_config['WINDOW_WIDTH']
WINDOW_HEIGHT = base_config['WINDOW_HEIGHT']
WINDOW_WALL_WIDTH = Window.WALL_WIDTH.value
GRID_SPACING = base_config['GRID_SPACING']

GRASS_SPEED = base_config['GRASS_SPEED']
WATER_SPEED = base_config['WATER_SPEED']


class Map:
    """Game map related methods."""

    nodes = set()  # All traversable nodes.
    # Game objects to load and associated attributes to calcuate
    # object positions.
    all_obj_attributes = []
    reduced_speed_nodes = {}  # Nodes in grass or water.
    blocked_nodes = set()  # Non-traversable nodes (in use by objects).

    window_width = WINDOW_WIDTH - WINDOW_WALL_WIDTH
    sprites_config = get_sprites_config_dict()

    def __init__(
        self,
        seed_: int = None,
        map_name: str = 'random',
        save: bool = True
    ):
        self.map_name = map_name
        self.save = save

        if seed_:
            seed(seed_)

        self._set_available_nodes()
        self._generate_map()

    def _set_available_nodes(self) -> None:
        """ Available nodes: all nodes on the screen."""
        for x in range(0, self.window_width, GRID_SPACING):
            for y in range(0, WINDOW_HEIGHT, GRID_SPACING):
                self.nodes.add((x, y))

    def _generate_map(self) -> None:
        """Generate a map from a list of sprites."""
        obj_names = self._objects_to_create_from_config()

        for obj_name in obj_names:
            obj_sprite = self.sprites_config[obj_name]['img']

            obj = Object(obj_name, obj_sprite)

            obj.set_dimensions()

            # Ensure the object does not touch any other objects.
            available_nodes = obj.avaialable_nodes() - self.blocked_nodes

            obj.xy = random_xy(available_nodes)
            obj.x, obj.y = obj.xy

            obj.find_available_position(available_nodes)

            # We ran out of nodes to check. There are no more positions
            # available for the object.
            if not available_nodes:
                break

            obj.set_perimeter()
            obj.set_nodes()
            obj.update_all_obj_attributes()

        self._update_nodes()

        print('You generated a new map!')

        if self.save:
            self._save()

    def _objects_to_create_from_config(self) -> list:
        obj_names = []

        for obj_name, obj_config in self.sprites_config.items():
            for quantity in range(obj_config['quantity']):
                obj_names.append(obj_name)

        return obj_names

    def _update_nodes(self) -> None:
        """Update available nodes for pathfinding to exclude nodes used
        by objects (non-traversable).
        """
        self.nodes = {n for n in self.nodes if n not in self.blocked_nodes}

    def _save(self) -> None:
        """Save map to .pkl in the maps/ directory."""
        cache_path = f'maps/{self.map_name}.pkl'

        del self.all_obj_attributes['width']
        del self.all_obj_attributes['height']

        map_ = {
            'nodes': self.nodes,
            'reduced speed nodes': self.reduced_speed_nodes,
            'objects': self.all_obj_attributes,
            'blocked nodes': self.blocked_nodes
        }
        with open(cache_path, 'wb') as path:
            pickle.dump(map_, path)

        print(f'New map "{self.map_name}" saved to {cache_path}.')

    @classmethod
    def load(cls, map_name: str) -> None:
        """Load a map from the maps/ directory."""
        with open(f'maps/{map_name}.pkl', 'rb') as path:
            map_ = pickle.load(path)
        cls.nodes = map_['nodes']
        cls.reduced_speed_nodes = map_['reduced speed nodes']
        cls.objects = map_['objects']
        cls.blocked_nodes = map_['blocked nodes']

        print(f'loaded map: {map_name}.')

    @classmethod
    def draw(cls, win: Sprite) -> None:
        for obj in cls.objects:
            loaded_object = cls.sprites_config[obj['name']]['img']
            x, y = obj['x'], obj['y']
            win.blit(loaded_object, (x, y))


class Object(Map):
    """Handle methods for the objects to be placed on the map."""

    def __init__(self, name: str, sprite: Sprite):
        self.name = name
        self.sprite = sprite

    def set_dimensions(self) -> None:
        """Set object dimensions according to our grid."""
        self.width = sync_value_with_grid(self.sprite.get_width())
        self.height = sync_value_with_grid(self.sprite.get_height())

        self.square_width = int(self.width / GRID_SPACING)
        self.square_height = int(self.height / GRID_SPACING)

    def avaialable_nodes(self) -> Set[tuple]:
        """All the nodes we can position the object at in order to
        keep the object on the screen.
        """
        nodes = set()
        for x in range(0, self.window_width - self.width, GRID_SPACING):
            for y in range(0, WINDOW_HEIGHT - self.height, GRID_SPACING):
                nodes.add((x, y))

        return nodes

    def set_perimeter(self) -> None:
        """Set all the coordinates making up the object's permiter."""
        self.perimeter_x = [
            self.x + (i * GRID_SPACING) for i in range(self.square_width)
        ]
        self.perimeter_y = [
            self.y + (i * GRID_SPACING) for i in range(self.square_height)
        ]

    def set_nodes(self) -> None:
        """Set coords used by object as non-traversable or set the
        associated movement cost if we are in grass or water.
        """
        for x in self.perimeter_x:
            for y in self.perimeter_y:
                if self.name == 'grass':
                    self.reduced_speed_nodes[(x, y)] = GRASS_SPEED
                elif self.name == 'water':
                    self.reduced_speed_nodes[(x, y)] = WATER_SPEED
                else:
                    self.blocked_nodes.add((x, y))

    def find_available_position(self, available_nodes: Set[tuple]) -> None:
        """Keep looking for new coords until the object no longer
        touches another object.
        """
        colliding = True
        if self.all_obj_attributes:
            while(colliding and available_nodes):
                for attributes in self.all_obj_attributes:
                    # The relative position of the new object compared
                    # to other objects already created.
                    rules = [
                        (self.x + self.width) < attributes['x'],
                        self.x > (attributes['x'] + attributes['width']),
                        (self.y + self.height) < attributes['y'],
                        self.y > (attributes['y'] + attributes['height'])
                    ]
                    #  This means we are not colliding with anything.
                    if any(rules):
                        failed = False
                    else:  # Colliding: choose a new x,y pair.
                        failed = True
                        available_nodes.remove(self.xy)
                        if not available_nodes:
                            break
                        self.xy = random_xy(available_nodes)
                        self.x, self.y = self.xy
                        break

                colliding = False if not failed else True

    def update_all_obj_attributes(self) -> None:
        self.all_obj_attributes.append({
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        })
