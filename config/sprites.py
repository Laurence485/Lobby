from utils import load_map_img


def sprites() -> dict:
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
