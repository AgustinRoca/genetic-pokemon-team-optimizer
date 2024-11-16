import random
from tqdm import tqdm

from utils.team import Team
from parse_csv import parse_csvs
from utils.combat import get_winner

def get_random_pokemon_for_team(pokemons_in_team, pokemons):
    new_pokemon = random.choice(list(pokemons.values()))
    while new_pokemon.name in [pokemon.name for pokemon in pokemons_in_team]:
        new_pokemon = random.choice(list(pokemons.values()))
    return new_pokemon

def get_random_team(team_name, pokemons, pokemons_per_team = 6):
    pokemons_for_team = []
    for pokemon_number in range(pokemons_per_team):
        new_pokemon = get_random_pokemon_for_team(pokemons_for_team, pokemons)
        pokemons_for_team.append(new_pokemon)
    return Team(team_name, pokemons_for_team)

def do_tournament(teams, testing_teams, effectiveness):
    results = {team: 0 for team in teams}
    for i in tqdm(range(len(teams))):
        for j in range(len(testing_teams)):
            if i != j:
                winner = get_winner(teams[i], testing_teams[j], effectiveness)
                if winner in teams:
                    results[winner] += 1
    results = list(results.items())
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def count_pokemons(teams):
    pokemon_counts = {}
    for team in teams:
        for pokemon in team.pokemons:
            if pokemon.name not in pokemon_counts:
                pokemon_counts[pokemon.name] = 0
            pokemon_counts[pokemon.name] += 1
    return pokemon_counts

def main():
    pokemons, effectiveness = parse_csvs(include_legendaries=False)

    teams_size = 50
    random_teams = 400
    pokemons_per_team = 6
    epochs = 50
    mutation_rate = 0.03
    change_starter_rate = 0.03
    mantain_best = 10

    teams = []
    team_num = 0
    for i in range(teams_size):
        team_num = i
        teams.append(get_random_team(f'Team {team_num}', pokemons, pokemons_per_team))

    with open('results/epochs.csv', 'w') as f:
        f.write('')

    with open('results/best_teams.csv', 'w') as f:
        f.write('')

    with open('results/starters.csv', 'w') as f:
        f.write('')

    for epoch in tqdm(range(epochs)):
        pokemon_counts = count_pokemons(teams)

        with open('results/epochs.csv', 'a') as f:
            diversity = len(pokemon_counts)
            top_pokemons = sorted(pokemon_counts, key=pokemon_counts.get, reverse=True)
            f.write(f'{epoch},{diversity},{",".join([pokemon + "," + str(pokemon_counts[pokemon]) for pokemon in top_pokemons])}\n')

        with open('results/best_teams.csv', 'a') as f:
            for team in teams:
                f.write(f'{epoch},{team.name},{team.current_pokemon_index},{",".join([pokemon.name for pokemon in team.pokemons])}\n')

        starters_counts = {}
        for team in teams:
            if team.get_current_pokemon().name not in starters_counts:
                starters_counts[team.get_current_pokemon().name] = 0
            starters_counts[team.get_current_pokemon().name] += 1

        with open('results/starters.csv', 'a') as f:
            sorted_starters = sorted(starters_counts, key=starters_counts.get, reverse=True)
            f.write(f'{epoch},{",".join([pokemon + "," + str(starters_counts[pokemon]) for pokemon in sorted_starters])}\n')
    
        random_pool = []
        for i in range(random_teams):
            random_pool.append(get_random_team(f'Random team {i}', pokemons, pokemons_per_team))

        results = do_tournament(teams, random_pool, effectiveness)
        winners = results[:mantain_best]
        winners = [team for team, wins in winners]

        new_teams = []
        new_teams.extend(winners)
        
        for i in range(teams_size - mantain_best):
            # crossover
            parent1, parent2 = random.choices(results, weights=[wins for team, wins in results], k=2)
            parent1, parent2 = parent1[0], parent2[0]
            
            
            if random.random() < 0.5:
                starter = parent1.current_pokemon_index
            else:
                starter = parent2.current_pokemon_index

            pokemons_for_team = []
            for pokemon1, pokemon2 in zip(parent1.pokemons, parent2.pokemons):
                pokemons_for_team_names = [pokemon.name for pokemon in pokemons_for_team]
                if pokemon1.name in pokemons_for_team_names and pokemon2.name not in pokemons_for_team_names:
                    pokemons_for_team.append(pokemon2)
                elif pokemon2.name in pokemons_for_team_names and pokemon1.name not in pokemons_for_team_names:
                    pokemons_for_team.append(pokemon1)
                elif pokemon1.name not in pokemons_for_team_names and pokemon2.name not in pokemons_for_team_names:
                    if random.random() < 0.5:
                        pokemons_for_team.append(pokemon1)
                    else:
                        pokemons_for_team.append(pokemon2)
                else:
                    pokemons_for_team.append(get_random_pokemon_for_team(pokemons_for_team, pokemons))

            # mutation
            if random.random() < change_starter_rate:
                starter = random.randint(0,pokemons_per_team-1)

            for change_pokemon in range(pokemons_per_team):
                if random.random() < mutation_rate:
                    new_pokemon = get_random_pokemon_for_team(pokemons_for_team, pokemons)
                    pokemons_for_team[change_pokemon] = new_pokemon

            team_num += 1
            new_teams.append(Team(f'Team {team_num}', pokemons_for_team, starter))
            
        teams = new_teams

if __name__ == '__main__':
    main()
