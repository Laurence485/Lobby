from utils import load_map_img


def sprites() -> dict:
    """Sprite dictionary used for generating new maps."""
    return {
        'bike shop': load_map_img('bikeShop'),
        'department store': load_map_img('departmentStore'),
        'door house': load_map_img('doorHouse'),
        'game corner': load_map_img('gameCorner'),
        'grass': load_map_img('grass_patch', 'jpg'),
        'mart': load_map_img('mart'),
        'oaks lab': load_map_img('oaksLab'),
        'water': load_map_img('pool'),
        'pokemon center': load_map_img('pokemonCenter'),
        'purple house': load_map_img('purpleHouse'),
        'tree': load_map_img('tree')
    }

    def objects_to_use_in_map(self):
        """Type and quantity of objects from config.sprites to use in
        map generation."""
        objects = {
            'bike shop': 0,
            'department store': 0,
            'door house': 0,
            'game corner': 0,
            'grass': 0,
            'mart': 0,
            'oaks lab': 0,
            'water': 0,
            'pokemon center': 0,
            'purple house': 0,
            'tree': 0
        }

        #  IF OBJECT KEYS NOT ALL IN DICT, RAISE ERROR.

        return objects
