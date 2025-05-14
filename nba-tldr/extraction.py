import pandas
from nba_api.stats.endpoints import playbyplayv3, boxscoresummaryv2, boxscoretraditionalv3, leaguegamefinder
from processing import join_player_names, process_team_stats

def get_actions(id):
    return playbyplayv3.PlayByPlayV3(game_id=id).get_data_frames()[0]

def get_box_score(id):
    box_score = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=id).get_data_frames()[0]
    return join_player_names(box_score)

def get_line_score(id):
    return boxscoresummaryv2.BoxScoreSummaryV2(game_id=id).get_data_frames()[5]

def get_other(id):
    return boxscoresummaryv2.BoxScoreSummaryV2(game_id=id).get_data_frames()[1]

def get_game_summary(id):
    return boxscoresummaryv2.BoxScoreSummaryV2(game_id=id).get_data_frames()[0]

def get_team_stats(id):
    other = get_other(id)
    line_score = get_line_score(id)
    game_summary = get_game_summary(id)

    team_stats = process_team_stats(other, line_score, game_summary)

    return team_stats