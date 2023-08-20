from itertools import combinations

import numpy as np
from ortools.sat.python import cp_model

if __name__ == "__main__":
    owners = [
        "corey",
        "fuzzy",
        "brendan",
        "robs",
        "robj",
        "james",
        "noah",
        "aaron",
        "aneesh",
        "kalani",
        "david",
        "grant",
    ]
    rivals = {
        "corey": "fuzzy",
        "fuzzy": "corey",
        "brendan": "noah",
        "noah": "brendan",
        "robj": "robs",
        "robs": "robj",
        "james": "aaron",
        "aaron": "james",
        "aneesh": "kalani",
        "kalani": "aneesh",
        "david": "grant",
        "grant": "david",
    }
    # conferences = [
    #     ("corey", "fuzzy", "brendan", "robs", "robj", "james"),
    #     ("brandon", "aaron", "aneesh", "kalani", "david", "grant"),
    # ]

    weeks = np.arange(1, 15)
    owner_ids = np.arange(0, len(owners))

    owner_id_combinations = combinations(owner_ids, 2)
    matchups = list(owner_id_combinations)

    model = cp_model.CpModel()
    # Create the decision variables
    games = {}
    for week in weeks:
        for id0, id1 in matchups:
            games[(week, id0, id1)] = model.NewBoolVar(
                f"{week}_{owners[id0]}_{owners[id1]}"
            )

    # Each team is assigned to one game per week
    for week in weeks:
        for owner_id in owner_ids:
            owner_games = []
            for id0, id1 in matchups:
                if owner_id == id0 or owner_id == id1:
                    owner_games.append(games[(week, id0, id1)])
            model.Add(sum(owner_games) == 1)

    # Each matchup happens at least once
    for id0, id1 in matchups:
        model.Add(sum([games[(week, id0, id1)] for week in weeks]) >= 1)

    # Each matchup happens no more than twice
    for id0, id1 in matchups:
        model.Add(sum([games[(week, id0, id1)] for week in weeks]) <= 2)

    # Rival matchups happen on the last week
    for id0, id1 in matchups:
        if rivals[owners[id0]] == owners[id1]:
            model.Add(games[(weeks[-1], id0, id1)] == 1)

    # Matchups don't happen two weeks in a row
    for week in weeks[:-1]:
        for id0, id1 in matchups:
            model.Add(games[(week, id0, id1)] + games[(week + 1, id0, id1)] <= 1)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 6
    solver.parameters.log_search_progress = False
    solver.Solve(model)
    owner_games = {}
    for owner in owners:
        owner_games[owner] = []
    game_names = []
    for week in weeks:
        for id0, id1 in matchups:
            if solver.Value(games[(week, id0, id1)]):
                game_name = f"Week {week}: {owners[id0]} vs {owners[id1]}"
                owner_games[owners[id0]].append(owners[id1])
                owner_games[owners[id1]].append(owners[id0])
                game_names.append(game_name)
                print(game_name)
        print("\n")

    for owner in owners:
        games_str = ""
        for i, opp in enumerate(owner_games[owner]):
            games_str += f"{i+1}-{opp}, "
        games_str = games_str[:-2]
        print(f"{owner}: {games_str}")
