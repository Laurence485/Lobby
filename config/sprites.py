from utils import load_map_img


def sprites() -> dict:
    """Sprite dictionary used for generating new maps."""
    return {
        'bike shop': {
            'img': load_map_img('bikeShop'),
            'quantity': 0
        },
        'department store': {
            'img': load_map_img('departmentStore'),
            'quantity': 0
        },
        'door house': {
            'img': load_map_img('doorHouse'),
            'quantity': 0
        },
        'game corner': {
            'img': load_map_img('gameCorner'),
            'quantity': 0
        },
        'grass': {
            'img': load_map_img('grass_patch', 'jpg'),
            'quantity': 0
        },
        'mart': {
            'img': load_map_img('mart'),
            'quantity': 0
        },
        'oaks lab': {
            'img': load_map_img('oaksLab'),
            'quantity': 0
        },
        'water': {
            'img': load_map_img('pool'),
            'quantity': 0
        },
        'pokemon center': {
            'img': load_map_img('pokemonCenter'),
            'quantity': 0
        },
        'purple house': {
            'img': load_map_img('purpleHouse'),
            'quantity': 0
        },
        'tree': {
            'img': load_map_img('tree'),
            'quantity': 0
        }
    }
