import matplotlib.pyplot as plt
from PIL import Image

def bw_image(pokemon):
    img = Image.open(f'data/imgs/{pokemon.pokedex_number:03d}.png')
    
    # convert transparent pixels to white
    img = img.convert('RGBA')
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[3] == 0:
            new_data.append((255, 255, 255, 255))
        else:
            new_data.append(item)
    img.putdata(new_data)
    
    # convert to black and white
    img = img.convert('L')
    
    return img

def draw_team_in_axes(team, imgs_ax, hp_ax):
    for i, pokemon in enumerate(team.pokemons):
        imgs_ax[i].set_title(pokemon.name)
        if pokemon.current_hp == 0:
            image = bw_image(pokemon)
            imgs_ax[i].imshow(image, cmap='gray')
        else:
            image = plt.imread(f'data/imgs/{pokemon.pokedex_number:03d}.png')
            imgs_ax[i].imshow(image)

        # frame around image if pokemon is active
        if i == team.current_pokemon_index:
            imgs_ax[i].set_frame_on(True)
            imgs_ax[i].patch.set_edgecolor('green')
            imgs_ax[i].patch.set_linewidth(5)
        else:
            imgs_ax[i].set_frame_on(False)

        imgs_ax[i].set_xticks([])
        imgs_ax[i].set_yticks([])
        
        
        hp_ax[i].barh(0, pokemon.current_hp, color='green')
        hp_ax[i].barh(0, pokemon.max_hp - pokemon.current_hp, left=pokemon.current_hp, color='red')
        hp_ax[i].axis('off')
        hp_ax[i].set_xlim(0, pokemon.max_hp)
        hp_ax[i].text(0.5, -0.5, f'{pokemon.current_hp:.2f}/{pokemon.max_hp:.2f}', size=12, ha='center', transform=hp_ax[i].transAxes)

def show_teams_status(team1, team2):
    # show 6 pokemons of each team, with HP bars. If a pokemon has 0 HP, show it in black and white
    pokemons_per_team = max(len(team1.pokemons), len(team2.pokemons))
    fig, axs = plt.subplots(4, pokemons_per_team, height_ratios=[1, 0.1, 1, 0.1], figsize=(12, 8))

    draw_team_in_axes(team1, axs[0], axs[1])
    draw_team_in_axes(team2, axs[2], axs[3])
    
    fig.suptitle(f'{team1.name} vs {team2.name}')
    fig.tight_layout()
    plt.show()
