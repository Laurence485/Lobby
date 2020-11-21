import pickle
import yaml
from random import seed
from config.sprites import sprites
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
    objects = []
    movement_cost_area = {}  # Movement has a cost - grass/water
    objs_area = set()  # Non-traversable nodes.

    def __init__(self, seed_: int = None):
        self.window_width = window_width - window_wall_width

        for x in range(0, self.window_width, grid_spacing):  # col
            for y in range(0, window_height, grid_spacing):  # row
                self.nodes.add((x, y))

        if seed_:
            seed(seed_)

    def generate_map(
        self,
        map_name: str = 'random',
        save: bool = False
    ) -> None:
        """Generate and save a map to .pkl from a list of sprites."""
        # Attributes (coordinates and dimensions) to calcuate object positions.
        obj_attributes = []
        obj_names = []

        for obj_name, obj_config in sprites().items():
            for quantity in range(obj_config['quantity']):
                obj_names.append(obj_name)

        for obj_name in obj_names:
            obj = sprites()[obj_name]['img']

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
            available_nodes = nodes_to_keep_obj_on_screen - self.objs_area

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

            self.objects.append([obj_name, rand_xy])

            obj_coords_x = [
                rand_x + (i * grid_spacing) for i in range(square_width)
            ]
            obj_coords_y = [
                rand_y + (i * grid_spacing) for i in range(square_height)
            ]

            # Get square area used by object or movement cost if grass/water
            for x in obj_coords_x:
                for y in obj_coords_y:
                    if obj_name == 'grass':
                        self.movement_cost_area[(x, y)] = 6
                    elif obj_name == 'water':
                        self.movement_cost_area[(x, y)] = 4
                    else:
                        self.objs_area.add((x, y))

            attributes = {
                'x': rand_x,
                'y': rand_y,
                'width': obj_width,
                'height': obj_height
            }
            obj_attributes.append(attributes)

        # Update available nodes for pathfinding to exclude nodes used
        # for objects.
        self.nodes = [n for n in self.nodes if n not in self.objs_area]
        obj_attributes.clear()

        if save:
            self.save(map_name)

    def save(self, map_name):
        """Save map to maps/ directory."""
        cache_path = f'maps/{map_name}.pkl'
        map_ = {
            'nodes': self.nodes,
            'mca': self.movement_cost_area,
            'objects': self.objects,
            'obj coords': self.objs_area
        }
        with open(cache_path, 'wb') as path:
            pickle.dump(map_, path)
        print(f'"{map_name}" saved to {cache_path}.')

    @classmethod
    def load(cls, map_name):
        """Load a map from the maps/ directory."""
        with open(f'maps/{map_name}.pkl', 'rb') as path:
            map_ = pickle.load(path)
        cls.nodes = map_['nodes']
        cls.movement_cost_area = map_['mca']
        cls.objects = map_['objects']
        cls.objs_area = map_['obj coords']

        print(f'loaded map: {map_name}.')
        # print(map_['objects'])

    @classmethod
    def draw(cls, win):
        for obj in cls.objects:
            loaded_object = sprites()[obj[0]]['img']
            x,y = obj[1]
            win.blit(loaded_object, (x,y))
