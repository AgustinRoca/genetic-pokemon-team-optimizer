import random

from gui import show_teams_status
from parse_csv import parse_best_teams, parse_csvs
from utils.team import Team

def faint_change_with_gui(team1: Team, team2: Team, effectiveness: dict[str, dict[str, float]]) -> None:
    if team1.get_current_pokemon().current_hp == 0:
        fainted_team = team1
        other_team = team2
    else:
        fainted_team = team2
        other_team = team1
    action_1, target_1 = fainted_team.get_next_action(other_team, effectiveness)
    fainted_team.do_action(action_1, target_1, other_team, effectiveness)
    show_teams_status(team1, team2)
    action_2, target_2 = other_team.get_next_action(fainted_team, effectiveness)
    if action_2 == 'switch':
        other_team.do_action(action_2, target_2, fainted_team, effectiveness)
        show_teams_status(team1, team2)

def fight_with_gui(team1: Team, team2: Team, effectiveness: dict[str, dict[str, float]]) -> None:
    turn = 0
    while any(pokemon.current_hp > 0 for pokemon in team1.pokemons) and any(pokemon.current_hp > 0 for pokemon in team2.pokemons):            
        action_1, target_1 = team1.get_next_action(team2, effectiveness)
        action_2, target_2 = team2.get_next_action(team1, effectiveness)

        # Switching always happens first
        if action_1 == 'switch':
            first = team1
            second = team2
        elif action_2 == 'switch':
            first = team2
            second = team1
            action_1, target_1, action_2, target_2 = action_2, target_2, action_1, target_1
        # If nobody is switching, the fastest pokemon goes firsts
        elif team1.get_current_pokemon().speed > team2.get_current_pokemon().speed:
            first = team1
            second = team2
        else:
            first = team2
            second = team1
            action_1, target_1, action_2, target_2 = action_2, target_2, action_1, target_1
    
        first.do_action(action_1, target_1, second, effectiveness)
        show_teams_status(team1, team2)
        
        # If any of the pokemons fainted, the turn ends, and both have the chance to switch
        if team1.get_current_pokemon().current_hp == 0 or team2.get_current_pokemon().current_hp == 0:
            faint_change_with_gui(team1, team2, effectiveness)
        else:
            if action_2 == 'attack' and target_2 is None:
                action_2, target_2 = second.get_next_action(first, effectiveness)
            second.do_action(action_2, target_2, first, effectiveness)
            show_teams_status(team1, team2)

            if team1.get_current_pokemon().current_hp == 0 or team2.get_current_pokemon().current_hp == 0:
                faint_change_with_gui(team1, team2, effectiveness)

        turn += 1
    
    return team1 if any(pokemon.current_hp > 0 for pokemon in team1.pokemons) else team2

pokemons, effectiveness = parse_csvs(include_legendaries=False)
teams = parse_best_teams(pokemons)[-1]
team1 = random.choice(teams)
team2 = random.choice(teams)

show_teams_status(team1, team2)
fight_with_gui(team1, team2, effectiveness)
