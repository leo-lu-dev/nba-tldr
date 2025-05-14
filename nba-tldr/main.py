import argparse
import extraction, processing, format

def process_game(game_id):
    actions = extraction.get_actions(game_id)
    box_score = extraction.get_box_score(game_id)
    team_stats = extraction.get_team_stats(game_id)

    actions = processing.process_scoring_actions(actions, box_score, team_stats)
    top_performers = processing.filter_top_performers(box_score)
    notable_periods = processing.filter_notable_periods(actions)
    clutch_plays = processing.filter_clutch_plays(actions)

    summary = format.get_summary(actions, top_performers, notable_periods, clutch_plays, team_stats, game_id)

    print(summary)

    return summary

def output_file(out, game_id, summary):
    with open(f'../data/formatted/{game_id}.txt', 'w', encoding='utf-8') as file:
        file.write(f"{summary}\n")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('game_id', type=str)
    parser.add_argument('--out', type=bool, required=False)

    args = parser.parse_args()

    summary = process_game(args.game_id)

    if args.out:
        output_file(args.out, args.game_id, summary)

if __name__ == '__main__':
    main()