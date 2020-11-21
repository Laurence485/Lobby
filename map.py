import pickle
import yaml

from config.sprites import config as sprites_config_dict
from random import seed
from typing_utils import Sprite
from utils import random_xy, sync_value_with_grid

with open('config/base.yaml', 'r') as config_file:
    config = yaml.load(config_file, yaml.Loader)

window_width = config['WINDOW_WIDTH']
window_height = config['WINDOW_HEIGHT']
window_wall_width = config['WINDOW_WALL_WIDTH']
grid_spacing = config['GRID_SPACING']


class Map:
    """Game map related methods."""

    nodes = set()  # All traversable nodes.
    objects = []  # List of game objects and coordinates (nodes).
    reduced_speed_nodes = {}  # Nodes in grass or water.
    blocked_nodes = set()  # Non-traversable nodes (in use by objects).

    sprites_config = sprites_config_dict()

    def __init__(
        self,
        seed_: int = None,
        map_name: str = 'random',
        save: bool = False
    ):
        self.window_width = window_width - window_wall_width
        self.map_name = map_name
        self.save = save

        for x in range(0, self.window_width, grid_spacing):  # col
            for y in range(0, window_height, grid_spacing):  # row
                self.nodes.add((x, y))

        if seed_:
            seed(seed_)

    def generate_map(self) -> None:
        """Generate and save a map to .pkl from a list of sprites."""
        # Attributes (coordinates and dimensions) to calcuate object positions.
        obj_attributes = []

        obj_names = self._objects_to_create_from_config()

        for obj_name in obj_names:
            obj = self.sprites_config[obj_name]['img']

            # Get object dimensions according to our grid
            obj_width = sync_value_with_grid(obj.get_width())
            obj_height = sync_value_with_grid(obj.get_height())
            square_width = int(obj_width / grid_spacing)
            square_height = int(obj_height / grid_spacing)

            # Keep objects on the screen.
            nodes_to_keep_obj_on_screen = set()
            for x in range(0, self.window_width - obj_width, grid_spacing):
                for y in range(0, window_height - obj_height, grid_spacing):
                    nodes_to_keep_obj_on_screen.add((x, y))

            # Ensure the object does not touch any other object.
            available_nodes = nodes_to_keep_obj_on_screen - self.blocked_nodes

            rand_xy = random_xy(available_nodes)
            rand_x, rand_y = rand_xy

            colliding = True
            if len(obj_attributes):
                while(colliding and len(available_nodes)):
                    for attributes in obj_attributes:
                        # The relative position of the new object compared
                        # to other objects already created.
                        rules = [
                            (rand_x + obj_width) < attributes['x'],
                            rand_x > (attributes['x'] + attributes['width']),
                            (rand_y + obj_height) < attributes['y'],
                            rand_y > (attributes['y'] + attributes['height'])
                        ]
                        #  This means we are not colliding with anything.
                        if any(rules):
                            failed = False
                        # Colliding: choose a new x,y pair.
                        else:
                            failed = True
                            available_nodes.remove(rand_xy)
                            if not(len(available_nodes)):
                                break
                            rand_xy = random_xy(available_nodes)
                            rand_x, rand_y = rand_xy
                            break

                    colliding = False if not failed else True

            if not(len(available_nodes)):
                break

            self.objects.append({'name': obj_name, 'coords': rand_xy})

            # Square area used by object
            obj_coords_x = [
                rand_x + (i * grid_spacing) for i in range(square_width)
            ]
            obj_coords_y = [
                rand_y + (i * grid_spacing) for i in range(square_height)
            ]

            # Coords used by objects are non-traversable or have an
            # associated movement cost i.e. in grass or water.
            for x in obj_coords_x:
                for y in obj_coords_y:
                    if obj_name == 'grass':
                        self.reduced_speed_nodes[(x, y)] = 6
                    elif obj_name == 'water':
                        self.reduced_speed_nodes[(x, y)] = 4
                    else:
                        self.blocked_nodes.add((x, y))

            obj_attributes.append({
                'x': rand_x,
                'y': rand_y,
                'width': obj_width,
                'height': obj_height
            })

        self._update_nodes()

        obj_attributes.clear()

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
        """Save map to maps/ directory."""
        cache_path = f'maps/{self.map_name}.pkl'
        map_ = {
            'nodes': self.nodes,
            'reduced speed nodes': self.reduced_speed_nodes,
            'objects': self.objects,
            'blocked nodes': self.blocked_nodes
        }
        with open(cache_path, 'wb') as path:
            pickle.dump(map_, path)

        print(f'"{self.map_name}" saved to {cache_path}.')

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
            x, y = obj['coords']
            win.blit(loaded_object, (x, y))
