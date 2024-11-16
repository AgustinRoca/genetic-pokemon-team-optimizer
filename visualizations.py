import matplotlib.pyplot as plt
import numpy as np
import os

from parse_csv import parse_csvs, parse_best_teams, parse_epochs
from utils.pokemon import TYPES, TYPES_COLORS

def draw_team(team):
    # show 6 pokemons of best team as images
    fig, axs = plt.subplots(2, 3, figsize=(8, 5))
    
    for i, pokemon in enumerate(team.pokemons):
        image_path = f'data/imgs/{pokemon.pokedex_number:03d}.png'
        image = plt.imread(image_path)
        axs[i//3, i%3].imshow(image)
        axs[i//3, i%3].axis('off')

        # add pokemon name under image
        axs[i//3, i%3].text(0.5, -0.15, pokemon.name, size=12, ha='center', transform=axs[i//3, i%3].transAxes)
        # add pokemon type under image, background color is the type color
        axs[i//3, i%3].text(0.2 if pokemon.type2 else 0.5, -0.35, f'{pokemon.type1}', size=12, ha='center', transform=axs[i//3, i%3].transAxes, backgroundcolor=TYPES_COLORS[TYPES.index(pokemon.type1)])
        if pokemon.type2:
            axs[i//3, i%3].text(0.8, -0.35, f'{pokemon.type2}', size=12, ha='center', transform=axs[i//3, i%3].transAxes, backgroundcolor=TYPES_COLORS[TYPES.index(pokemon.type2)])
        if i == team.current_pokemon_index:
            axs[i//3, i%3].text(0.5, -0.6, 'Starter', size=12, ha='center', transform=axs[i//3, i%3].transAxes)
    fig.suptitle(f'Best team: {team.name}')
    fig.tight_layout()
    plt.show()

def plot_radar_stats(team):
    # show stats of best team as radar plot, with each pokemon as a different color
    stats = [[pokemon.max_hp, pokemon.attack, pokemon.defense, pokemon.sp_attack, pokemon.sp_defense, pokemon.speed] for pokemon in team.pokemons]
    stats = np.array(stats)
    labels = ['Max HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats = np.concatenate((stats, stats[:,[0]]), axis=1)
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))
    for i, pokemon in enumerate(team.pokemons):
        ax.fill(angles, stats[i], alpha=0.25)
        ax.plot(angles, stats[i], label=pokemon.name)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))

    # add polar ticks
    max_stat = 400
    ax.set_ylim(0, max_stat)
    ax.set_yticks(list(range(100, max_stat+1, 100)))
    ax.set_yticklabels([str(i) for i in range(100, max_stat+1, 100)])


    fig.suptitle(f'Stats of best team: {team.name}')
    fig.tight_layout()
    plt.show()

def plot_diversity_vs_epochs(epochs):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([epoch['epoch'] for epoch in epochs], [epoch['diversity'] for epoch in epochs])
    ax.set_xlabel('Epochs')
    ax.set_ylabel('Diversity')
    ax.set_title('Diversity vs Epochs')
    plt.show()
    
def plot_pokemon_count_histogram(teams):
    pokemon_counts = {}
    for team in teams:
        for pokemon in team.pokemons:
            if pokemon.name not in pokemon_counts:
                pokemon_counts[pokemon.name] = 0
            pokemon_counts[pokemon.name] += 1

    #plot horizontal histogram with sorted pokemons
    fig, ax = plt.subplots(figsize=(6, 8))
    sorted_pokemons = sorted(pokemon_counts, key=pokemon_counts.get)
    ax.barh(sorted_pokemons, [pokemon_counts[pokemon] for pokemon in sorted_pokemons])
    ax.set_xlabel('Count')
    ax.set_ylabel('Pokemon')
    ax.set_title('Pokemon count in best teams')
    fig.tight_layout()
    plt.show()

def plot_pokemon_type_histogram(teams):
    type_counts = {}
    for team in teams:
        for pokemon in team.pokemons:
            type1 = pokemon.type1
            type2 = pokemon.type2
            if type1 not in type_counts:
                type_counts[type1] = 0
            type_counts[type1] += 1
            if type2:
                if type2 not in type_counts:
                    type_counts[type2] = 0
                type_counts[type2] += 1

    #plot horizontal histogram with sorted types
    fig, ax = plt.subplots(figsize=(6, 8))
    sorted_types = sorted(type_counts, key=type_counts.get)
    ax.barh(sorted_types, [type_counts[type] for type in sorted_types], color=[TYPES_COLORS[TYPES.index(type)] for type in sorted_types])
    ax.set_xlabel('Count')
    ax.set_ylabel('Type')
    ax.set_title('Type count in best teams')
    fig.tight_layout()
    plt.show()

def plot_pokemon_type_count_vs_epochs(epochs, pokemons_db):
    type_counts = []
    for epoch in epochs:
        type_counts_for_epoch = {}
        suma = 0
        for pokemon in epoch['pokemons']:
            suma += epoch['pokemons'][pokemon]
            type1 = pokemons_db[pokemon].type1
            type2 = pokemons_db[pokemon].type2
            if type1 not in type_counts_for_epoch:
                type_counts_for_epoch[type1] = 0
            type_counts_for_epoch[type1] += epoch['pokemons'][pokemon]
            if type2:
                if type2 not in type_counts_for_epoch:
                    type_counts_for_epoch[type2] = 0
                type_counts_for_epoch[type2] += epoch['pokemons'][pokemon]
        type_counts.append(type_counts_for_epoch)

    fig, ax = plt.subplots(figsize=(8, 6))
    # stack plot with types
    summed_counts = {type: sum([type_counts[i].get(type, 0) for i in range(len(epochs))]) for type in TYPES}
    sorted_types = sorted(summed_counts, key=summed_counts.get, reverse=True)
    colors = []
    for type in sorted_types:
        colors.append(TYPES_COLORS[TYPES.index(type)])
    stacked_counts = []
    for type in sorted_types:
        stacked_counts.append([type_counts[i].get(type, 0) for i in range(len(epochs))])
    stacked_counts = np.array(stacked_counts)
    # normalize stacked counts
    stacked_counts = stacked_counts / stacked_counts.sum(axis=0)
    ax.stackplot([epoch['epoch'] for epoch in epochs], stacked_counts, labels=sorted_types, colors=colors)

    ax.set_xlabel('Epochs')
    ax.set_ylabel('Count')
    ax.set_title('Type count vs Epochs')

    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
    fig.tight_layout()
    plt.show()

def plot_pokemon_type_count_vs_epochs_line(epochs, pokemons_db):
    type_counts = []
    for epoch in epochs:
        type_counts_for_epoch = {}
        suma = 0
        for pokemon in epoch['pokemons']:
            suma += epoch['pokemons'][pokemon]
            type1 = pokemons_db[pokemon].type1
            type2 = pokemons_db[pokemon].type2
            if type1 not in type_counts_for_epoch:
                type_counts_for_epoch[type1] = 0
            type_counts_for_epoch[type1] += epoch['pokemons'][pokemon]
            if type2:
                if type2 not in type_counts_for_epoch:
                    type_counts_for_epoch[type2] = 0
                type_counts_for_epoch[type2] += epoch['pokemons'][pokemon]
        type_counts.append(type_counts_for_epoch)

    fig, ax = plt.subplots(figsize=(8, 6))
    # line plot with types
    for type in TYPES:
        x = [epoch['epoch'] for epoch in epochs]
        y = [type_counts[i].get(type, 0) for i in range(len(epochs))]
        ax.plot(x, y, label=type, color=TYPES_COLORS[TYPES.index(type)])
        ax.fill_between(x, y, color=TYPES_COLORS[TYPES.index(type)], alpha=0.25)

    ax.set_xlabel('Epochs')
    ax.set_ylabel('Count')
    ax.set_title('Type count vs Epochs')

    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
    fig.tight_layout()
    plt.show()
    
def main():
    pokemons, effectiveness = parse_csvs(include_legendaries=False)
    
    best_teams_path = 'results/best_teams.csv' if os.path.exists('results/best_teams.csv') else 'results/best_teams_example.csv'
    epochs_path = 'results/epochs.csv' if os.path.exists('results/epochs.csv') else 'results/epochs_example.csv'

    teams = parse_best_teams(pokemons, best_teams_path)
    epochs = parse_epochs(epochs_path)

    draw_team(teams[-1][0])
    plot_radar_stats(teams[-1][0])
    plot_diversity_vs_epochs(epochs)
    plot_pokemon_count_histogram(teams[-1])
    plot_pokemon_type_histogram(teams[-1])
    plot_pokemon_type_count_vs_epochs(epochs, pokemons)
    plot_pokemon_type_count_vs_epochs_line(epochs, pokemons)

if __name__ == '__main__':
    main()
