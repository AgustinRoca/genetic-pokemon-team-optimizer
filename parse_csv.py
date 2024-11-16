from utils.pokemon import Pokemon, TYPES
from utils.team import Team

def parse_csv(filename, key_column, int_columns=[], float_columns=[], bool_columns=[], list_columns=[]):
    data = {}
    with open(filename) as f:
        header = f.readline().strip().split(',')
        for line in f:
            line = line.strip().split(',')
            line = dict(zip(header, line))
            key = line[key_column]
            line.pop(key_column)
            for column in int_columns:
                line[column] = int(line[column])
            for column in float_columns:
                if line[column] == '':
                    line[column] = 0.0
                else:
                    line[column] = float(line[column])
            for column in bool_columns:
                line[column] = bool(int(line[column]))
            for column in list_columns:
                line[column] = line[column].split(';')
            data[key] = line
    return data

def parse_csvs(pokemons_csv='data/pokemons.csv', moves_csv='data/moves.csv', effectiveness_csv='data/effectiveness_chart.csv', include_legendaries=True):
    pokemons_data = parse_csv(
        pokemons_csv,
        'name',
        int_columns=['pokedex_number', 'generation', 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed'],
        float_columns=['weight_kg', 'height_m'],
        bool_columns=['is_legendary'],
        list_columns=['moves']
    )

    moves_data = parse_csv(
        moves_csv,
        'name',
        int_columns=['pp', 'power', 'accuracy']
    )

    pokemons = {}
    for name, data in pokemons_data.items():
        pokemons[name] = Pokemon.from_dict(name, data, moves_data)

    effectiveness = parse_csv(
        effectiveness_csv,
        'attacking',
        float_columns=TYPES
    )
    if not include_legendaries:
        pokemons = {name: pokemon for name, pokemon in pokemons.items() if not pokemon.is_legendary}
    return pokemons, effectiveness

def parse_best_teams(pokemons_db, csv_file = 'results/best_teams.csv'):
    epochs = []
    teams = []
    last_epoch = 0
    with open(csv_file) as f:
        f.readline()
        for line in f:
            line = line.strip().split(',')
            epoch = int(line[0])
            if epoch != last_epoch:
                epochs.append(teams)
                teams = []
                last_epoch = epoch
            team_name = line[1]
            starter_index = int(line[2])
            pokemons = [pokemons_db[pokemon_name] for pokemon_name in line[3:]]
            team = Team(team_name, pokemons, starter_index)
            teams.append(team)
    return epochs

def parse_epochs(csv_file = 'results/epochs.csv'):
    epochs = []
    with open(csv_file) as f:
        for line in f:
            epoch = {}
            line = line.strip().split(',')
            epoch['epoch'] = int(line[0])
            epoch['diversity'] = int(line[1])
            epoch['pokemons'] = {}
            for pokemon, count in zip(line[2::2], line[3::2]):
                epoch['pokemons'][pokemon] = int(count)
            epochs.append(epoch)
    return epochs

def parse_starters(csv_file = 'results/starters.csv'):
    starters = []
    with open(csv_file) as f:
        epoch = {}
        for line in f:
            line = line.strip().split(',')
            epoch['epoch'] = int(line[0])
            for pokemon, count in zip(line[1::2], line[2::2]):
                epoch['pokemons'][pokemon] = int(count)
    return starters
