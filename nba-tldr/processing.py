import pandas

def join_player_names(box_score):
    box_score['fullName'] = box_score['firstName'] + ' ' + box_score['familyName']
    box_score.drop(['firstName', 'familyName'], axis=1, inplace=True)

    return box_score

def join_team_names(team_stats):
    team_stats['TEAM_NAME'] = team_stats['TEAM_CITY_NAME'] + ' ' + team_stats['TEAM_NICKNAME']
    team_stats.drop(['TEAM_CITY_NAME', 'TEAM_NICKNAME'], axis=1, inplace=True)
    return team_stats

def process_team_stats(other, line_score, game_summary):
    team_stats = line_score.merge(other[['TEAM_ID', 'LARGEST_LEAD', 'LEAD_CHANGES', 'TIMES_TIED']], on='TEAM_ID', how='left')
    team_stats = join_team_names(team_stats)
    team_stats['home'] = team_stats['TEAM_ID'] == game_summary['HOME_TEAM_ID'].iloc[0]

    return team_stats

def get_home_away_stats(team_stats):
    home_stats = team_stats[team_stats['home']]
    away_stats = team_stats[~team_stats['home']]

    return home_stats, away_stats

def get_team_names(team_stats):
    home_stats, away_stats = get_home_away_stats(team_stats)

    home_team_name = home_stats['TEAM_NAME'].iloc[0]
    home_tricode = home_stats['TEAM_ABBREVIATION'].iloc[0]
    away_team_name = away_stats['TEAM_NAME'].iloc[0]
    away_tricode = away_stats['TEAM_ABBREVIATION'].iloc[0]

    return home_team_name, home_tricode, away_team_name, away_tricode

def filter_top_performers(box_score):
    return box_score.sort_values(['points', 'assists', 'reboundsTotal'], ascending=False).groupby('teamId').head(3)

def filter_scoring_actions(actions):
    actions.sort_values(by=['actionNumber'], inplace=True)
    scoring_actions = actions[(actions['pointsTotal'] != 0) & (actions['actionType'] != 'period')] #filter out nonscoring plays

    return scoring_actions

def merge_team_player_names(actions, box_score, team_stats):
    actions = actions.merge(box_score[['personId', 'fullName']],
                                             on='personId', 
                                             how='left')
    actions = actions.merge(team_stats[['TEAM_ID', 'TEAM_NAME', 'home']],
                                             left_on='teamId',
                                             right_on='TEAM_ID', 
                                             how='left')
    
    return actions
    
def set_scoring_flags(scoring_actions, home_team_name, away_team_name):
    scoring_actions['pointsScored'] = scoring_actions['pointsTotal'] - scoring_actions['pointsTotal'].shift(1, fill_value=0)
    scoring_actions['leader'] = scoring_actions.apply(
        lambda row: away_team_name if int(row['scoreAway']) > int(row['scoreHome'])
        else home_team_name if int(row['scoreHome']) > int(row['scoreAway'])
        else 'Tied', axis=1
    )
    scoring_actions['leadChangeOrTie'] = scoring_actions['leader'] != scoring_actions['leader'].shift(1, fill_value=False)

    return scoring_actions

def process_scoring_actions(actions, box_score, team_stats):
    scoring_actions = filter_scoring_actions(actions)
    scoring_actions = merge_team_player_names(scoring_actions, box_score, team_stats)
    home_team_name, _, away_team_name, _ = get_team_names(team_stats)
    scoring_actions = set_scoring_flags(scoring_actions, home_team_name, away_team_name)
    scoring_actions = actions_cleanup(scoring_actions)

    return scoring_actions

def actions_cleanup(actions):
    actions.drop([ 'actionNumber',
               'actionType',
               'playerName',
               'playerNameI', 
               'xLegacy', 
               'yLegacy', 
               'shotDistance', 
               'shotResult', 
               'isFieldGoal', 
               'location', 
               'subType', 
               'videoAvailable', 
               'shotValue', 
               'actionId',
               'teamId',#
               'personId',#
               'pointsTotal'] #
               , axis=1, inplace=True)
    
    return actions

def filter_notable_periods(scoring_actions):
    notable_periods = scoring_actions.groupby(['period', 'fullName'], as_index=False).agg({'pointsScored':'sum'})
    notable_periods = notable_periods[notable_periods['pointsScored'] >= 15].reset_index() #identify periods where players scored 10+ points

    return notable_periods

def filter_clutch_plays(scoring_actions):
    clutch_plays = scoring_actions[
    (scoring_actions['clock'].str[2:4].astype(int) < 5) & 
    (scoring_actions['period'].astype(int) >= 4) & 
    scoring_actions['leadChangeOrTie']] #less than 5 mins left in Q4 or OT and score within 5

    return clutch_plays
