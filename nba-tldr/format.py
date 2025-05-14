import pandas
import processing

GAME_TYPE_INDEX = 2

#Game types
PRESEASON = 1
REGULAR_SEASON = 2
ALLSTAR = 3
PLAYOFFS = 4
PLAYIN = 5
CUPFINAL = 6

#2001-02 season to present
PLAYOFF_ROUND = -3 
SERIES_GAME = -1

#1996-97 to 2000-01, some discrepancies in format, less reliable (some games are logged backwards)
FIRST_ROUND_BEGIN = 1
FIRST_ROUND_END = 40
CONF_SEMI_BEGIN = 41
CONF_SEMI_END = 68
CONF_FINALS_BEGIN = 69
CONF_FINALS_END = 82
FINALS_BEGIN = 83
FINALS_END = 89

def get_game_date(team_stats):
    return f"{team_stats['GAME_DATE_EST'].iloc[0][0:10]}\n"

def get_playoff_old(playoff_game_number):
    

    if FIRST_ROUND_BEGIN <= playoff_game_number < FIRST_ROUND_END:
        playoff_round = 'First Round'
        series_game_number = int((playoff_game_number - FIRST_ROUND_BEGIN + 8) / 8)
    elif CONF_SEMI_BEGIN <= playoff_game_number < CONF_SEMI_END:
        playoff_round = 'Conference Semifinal'
        series_game_number = int((playoff_game_number - CONF_SEMI_BEGIN + 4) / 4)
    elif CONF_FINALS_BEGIN <= playoff_game_number < CONF_FINALS_END:
        playoff_round = 'Conference Finals'
        series_game_number = int((playoff_game_number - CONF_FINALS_BEGIN + 2) / 2)
    elif FINALS_BEGIN <= playoff_game_number < FINALS_END:
        playoff_round = 'NBA Finals'
        series_game_number = playoff_game_number - FINALS_BEGIN + 1
    game_context = playoff_round + " Game " + str(series_game_number)

    return game_context

def get_playoff_new(playoff_round_number, series_game_number):
    if playoff_round_number == '1':
        playoff_round = 'First Round'
    elif playoff_round_number == '2':
        playoff_round = 'Conference Semifinal'
    elif playoff_round_number == '3':
        playoff_round = 'Conference Finals'
    elif playoff_round_number == '4':
        playoff_round = 'NBA Finals'
    game_context = playoff_round + ' Game ' + str(series_game_number)

    return game_context

def get_playoff_round(id):
    year = int(id[3:5])
    if year >= 96:
        playoff_game_number = int(id[-2:])
        return get_playoff_old(playoff_game_number)
    else:
        playoff_round_number = id[PLAYOFF_ROUND]
        series_game_number = id[SERIES_GAME]
        return get_playoff_new(playoff_round_number, series_game_number)

def get_game_context(id):
    game_type = int(id[GAME_TYPE_INDEX])

    if game_type == PRESEASON:
        game_context = 'Preseason'
    elif game_type == REGULAR_SEASON:
        game_context = 'Regular Season'
    elif game_type == ALLSTAR:
        game_context = 'All-Star'
    elif game_type == PLAYOFFS:
        game_context = get_playoff_round(id)
    elif game_type == PLAYIN:
        game_context = 'Play-In' 
    elif game_type == CUPFINAL:
        game_context = 'NBA Cup Final'
    else:
        game_context = '' 
    
    return f"{game_context}\n\n"

def get_period_pts_str(period, home_team_name, away_team_name, home_stats, away_stats):
    if period <= 4:
        period_str = 'Q' + str(period)
        pts_str = 'PTS_QTR' + str(period)
    else:
        period_str = str(period - 4) + 'OT'
        pts_str = 'PTS_OT' + str(period - 4)

    return f"{period_str}:\n{home_team_name} {home_stats[pts_str].iloc[0]}-{away_stats[pts_str].iloc[0]} {away_team_name}\n"

def get_period_performance_str(period, notable_periods):
    period_performance_str = []

    period_performances = notable_periods[notable_periods['period'] == period]

    if len(period_performances) > 0:
        period_performance_str.append('NOTABLE PERIODS:\n')
        for _, row in period_performances.iterrows():
            period_performance_str.append(f"{row['fullName']} scores {row['pointsScored']} points\n")
    
    return ''.join(period_performance_str)

def get_period_clutch_str(period, clutch_plays, home_tricode, away_tricode):
    period_clutch_str = []

    period_clutch_plays = clutch_plays[clutch_plays['period'] == period]

    if period >= 4 and len(period_clutch_plays) > 0:
        period_clutch_str.append('CLUTCH PLAYS:\n')
        for _, row in period_clutch_plays.iterrows():
            period_clutch_str.append(f"({row['teamTricode']}) {row['clock'][2:4]}:{row['clock'][5:10]} {row['description']}  ({home_tricode} {row['scoreHome']}-{row['scoreAway']} {away_tricode})\n")
    
    return ''.join(period_clutch_str)

def get_period_summaries(actions, notable_periods, clutch_plays, home_team_name, home_tricode, away_team_name, away_tricode, home_stats, away_stats):
    period_summaries = []
    
    for period in actions['period'].unique():
        period_pts_str = get_period_pts_str(period, home_team_name, away_team_name, home_stats, away_stats)
        period_performance_str = get_period_performance_str(period, notable_periods)
        period_clutch_str = get_period_clutch_str(period, clutch_plays, home_tricode, away_tricode)
        period_summaries.append(period_pts_str + period_performance_str + period_clutch_str + '\n')

    return ''.join(period_summaries)

def get_game_stats(home_team_name, away_team_name, home_stats, away_stats, id):
    game_stats = [f"FINAL:\n{home_team_name} {home_stats['PTS'].iloc[0]}-{away_stats['PTS'].iloc[0]} {away_team_name}\n"]

    if int(id[GAME_TYPE_INDEX]) == PLAYOFFS and home_stats['TEAM_WINS_LOSSES'].iloc[0]: #is a playoff game and series score exists
        game_stats.append(f"SERIES:\n{home_team_name} {home_stats['TEAM_WINS_LOSSES'].iloc[0]} {away_team_name}\n")
    game_stats.append(f"LARGEST LEAD:\n{home_team_name} {home_stats['LARGEST_LEAD'].iloc[0]}-{away_stats['LARGEST_LEAD'].iloc[0]} {away_team_name}\n")
    game_stats.append(f"LEAD CHANGES:\n{home_stats['LEAD_CHANGES'].iloc[0]}\n")
    game_stats.append(f"TIMES TIED: \n{home_stats['TIMES_TIED'].iloc[0]}\n")

    return ''.join(game_stats)

def get_top_performers(top_performers):
    top_performers_str = [f"TOP PERFORMERS:\n{'Name':<20} {'Team':<6} {'Min':<6} {'PTS':<6} {'REB':<6} {'AST':<6}\n"]
    top_performers_str.append('-' * 52 + '\n')
    for _, row in top_performers.iterrows():
        top_performers_str.append(f"{row['fullName']:<20} {row['teamTricode']:<6} {row['minutes'][0:2]:<6} {row['points']:<6} {row['reboundsTotal']:<6} {row['assists']:<6}\n")
        
    return ''.join(top_performers_str)

def get_summary(actions, top_performers, notable_periods, clutch_plays, team_stats, id):
    home_team_name, home_tricode, away_team_name, away_tricode = processing.get_team_names(team_stats)
    home_stats, away_stats = processing.get_home_away_stats(team_stats)

    summary = get_game_date(team_stats) + \
                get_game_context(id) + \
                get_period_summaries(actions, notable_periods, clutch_plays, home_team_name, home_tricode, \
                                     away_team_name, away_tricode, home_stats, away_stats) + \
                get_game_stats(home_team_name, away_team_name, home_stats, away_stats, id) + \
                get_top_performers(top_performers)

    return summary