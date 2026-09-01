import streamlit as st
import pandas as pd
import pymysql
from pathlib import Path

conn = pymysql.connect(host="localhost", user="root", password="1234", database="nhl_project")
cursor = conn.cursor()

st.markdown(
	"""
	<style>
	[data-testid="stSidebar"] {
		background: #eef3f6;
	}
	[data-testid="stSidebarContent"] {
		padding: 1.5rem 1rem;
	}
	.sidebar-brand {
		background: #ffffff;
		border-radius: 8px;
		padding: 1.2rem 1rem;
		font-size: 1.35rem;
		font-weight: 600;
		color: #30343b;
		margin-bottom: 0.75rem;
	}
	[data-testid="stRadio"] > div {
		gap: 0.25rem;
	}
	[data-testid="stRadio"] label {
		border-radius: 6px;
		padding: 0.7rem 0.8rem;
		color: #30343b;
		font-size: 1rem;
		font-weight: 700 !important;
	}
	[data-testid="stRadio"] label p,
	[data-testid="stRadio"] label span {
		font-weight: 700 !important;
	}
	[data-testid="stRadio"] label:has(input:checked) {
		background: #1976d2;
		color: #ffffff;
		font-weight: 700 !important;
	}
	[data-testid="stRadio"] label > div:first-child {
		display: none;
	}
	[data-testid="stMetric"] {
		border: 1px solid #d9dee3;
		border-radius: 8px;
		padding: 0.8rem;
		background: #ffffff;
		min-height: 7.5rem;
	}
	[data-testid="stMetricLabel"] {
		font-size: 0.85rem !important;
		font-weight: 700 !important;
	}
	[data-testid="stMetricLabel"] p {
		font-weight: 700 !important;
	}
	[data-testid="stMetricValue"] {
		font-size: 1.25rem !important;
		line-height: 1.15 !important;
		white-space: normal !important;
		overflow: visible !important;
		overflow-wrap: break-word !important;
		word-break: normal !important;
		text-overflow: clip !important;
	}
	[data-testid="stMetricValue"] > div {
		white-space: normal !important;
		overflow: visible !important;
		text-overflow: clip !important;
	}
	.home-title {
		text-align: center;
		white-space: nowrap;
		font-weight: 700;
	}
	h1, h2, h3 {
		font-weight: 700 !important;
	}
	</style>
	""",
	unsafe_allow_html=True,
)

st.sidebar.markdown(
	"<div class='sidebar-brand'>🏒 NHL Hockey Analytics Dashboard</div>",
	unsafe_allow_html=True,
)

menu = [
	"⌂  Home",
	"☷  Standings",
	"♧  Team Info",
	"⌕  Player Search",
	"⌁  Match Results",
	"▥  Leaderboards",
	"</>  SQL Query",
]
page = st.sidebar.radio("Match Results", menu, label_visibility="collapsed")

if page == "⌂  Home":
	image, heading = st.columns([1, 2])
	image.image(
		Path(__file__).resolve().parent / "hockey-1689929962.jpg",
		width="stretch",
	)
	heading.markdown(
		"<h1 class='home-title' style='font-size: 2rem;'>"
		"🏒 NHL Hockey Analytics Dashboard"
		"</h1>"
		"<p style='text-align: center;'>"
		"API-driven hockey data with SQL analysis and dashboard"
		"</p>",
		unsafe_allow_html=True,
	)

	def get_value(sql):
		cursor.execute(sql)
		value = cursor.fetchone()[0]
		return value if value is not None else "N/A"

	def show_cards(cards, number_format=False):
		for column, (label, value) in zip(st.columns(4), cards):
			if number_format:
				value = f"{value:,}"
			column.metric(label, value)

	show_cards([
		("Total Teams", get_value("SELECT COUNT(*) FROM teams")),
		("Total Players", get_value("SELECT COUNT(*) FROM players")),
		("Total Games", get_value("SELECT COUNT(DISTINCT game_id) FROM game_stats")),
		("Total Goals", get_value("SELECT COALESCE(SUM(goals), 0) FROM game_stats")),
	], number_format=True)

	show_cards([
		("Top Scorer", get_value(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) "
			"FROM skater_stats s JOIN players p ON p.player_id = s.player_id "
			"ORDER BY s.goals DESC LIMIT 1"
		)),
		("Best Goal Saver", get_value(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) "
			"FROM goalie_season_stats g JOIN players p ON p.player_id = g.player_id "
			"WHERE g.save_pct IS NOT NULL ORDER BY g.save_pct DESC LIMIT 1"
		)),
		("League Leader Team", get_value(
			"SELECT t.team_name FROM standings s "
			"JOIN teams t ON t.team_id = s.team_id "
			"ORDER BY s.points DESC LIMIT 1"
		)),
		("Most Assists", get_value(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) "
			"FROM skater_stats s JOIN players p ON p.player_id = s.player_id "
			"ORDER BY s.assists DESC LIMIT 1"
		)),
	])

elif page == "☷  Standings":
	st.header("Standings")

	cursor.execute("SELECT DISTINCT conference_name FROM teams ORDER BY conference_name")
	conferences = [row[0] for row in cursor.fetchall() if row[0]]
	conference = st.selectbox("Conference", ["All Conferences"] + conferences)

	if conference == "All Conferences":
		cursor.execute("SELECT DISTINCT division_name FROM teams ORDER BY division_name")
	else:
		cursor.execute(
			"SELECT DISTINCT division_name FROM teams "
			"WHERE conference_name = %s ORDER BY division_name",
			(conference,),
		)
	divisions = [row[0] for row in cursor.fetchall() if row[0]]
	division = st.selectbox("Division", ["All Divisions"] + divisions)

	team_filter = st.radio(
		"Team Filter",
		["All Teams", "Select Range"],
		horizontal=True,
	)

	query = """
		SELECT
			t.logo_url AS Logo,
			t.team_name AS Team,
			t.conference_name AS Conference,
			t.division_name AS Division,
			s.games_played AS GP,
			s.wins AS W,
			s.losses AS L,
			s.ot_losses AS OT_L,
			s.points AS Points,
			s.goals_for AS GF,
			s.goals_against AS GA,
			s.home_wins AS Home_Wins,
			s.away_wins AS Away_Wins
		FROM standings s
		JOIN teams t ON t.team_id = s.team_id
	"""

	cursor.execute(query + " ORDER BY s.points DESC")

	rows = cursor.fetchall()
	columns = [column[0] for column in cursor.description]
	standings = pd.DataFrame(rows, columns=columns)

	if conference != "All Conferences":
		standings = standings[standings["Conference"] == conference]
	if division != "All Divisions":
		standings = standings[standings["Division"] == division]

	standings.insert(0, "Rank", range(1, len(standings) + 1))

	if team_filter == "Select Range" and not standings.empty:
		first_rank, last_rank = st.slider(
			"Select Rank Range",
			1,
			len(standings),
			(1, len(standings)),
		)
		standings = standings[
			standings["Rank"].between(first_rank, last_rank)
		]

	st.dataframe(
		standings,
		hide_index=True,
		width="stretch",
		column_config={
			"Logo": st.column_config.ImageColumn("Team Logo", width="small"),
		},
	)

elif page == "♧  Team Info":
	st.header("Team Info")

	cursor.execute(
		"SELECT team_name FROM teams ORDER BY team_name"
	)
	team_names = [row[0] for row in cursor.fetchall()]

	if team_names:
		selected_team = st.selectbox("Select Team", team_names)
		cursor.execute(
			"SELECT team_id, team_name, team_abbrev, conference_name, division_name, logo_url "
			"FROM teams WHERE team_name = %s",
			(selected_team,),
		)
		team = cursor.fetchone()
		cursor.execute(
			"SELECT games_played, wins, losses, ot_losses, points "
			"FROM standings WHERE team_id = %s ORDER BY season DESC LIMIT 1",
			(team[0],),
		)
		current_standing = cursor.fetchone()

		logo, details = st.columns([1, 3])
		with logo:
			if team[5]:
				st.image(team[5], width=160)
		with details:
			st.subheader(team[1])
			if current_standing:
				st.markdown(
					f"**Current Standings:** {current_standing[4]} points | "
					f"{current_standing[1]} W - {current_standing[2]} L - "
					f"{current_standing[3]} OT L | {current_standing[0]} GP"
				)
			st.write(f"**Abbreviation:** {team[2]}")
			st.write(f"**Conference:** {team[3]}")
			st.write(f"**Division:** {team[4]}")

		st.subheader("Team Roster")
		cursor.execute(
			"SELECT p.first_name, p.last_name, p.position, p.jersey_number, "
			"CAST(COALESCE(SUM(s.goals), 0) AS UNSIGNED) AS total_goals "
			"FROM players p "
			"LEFT JOIN skater_stats s ON s.player_id = p.player_id "
			"WHERE p.team_id = %s "
			"GROUP BY p.player_id, p.first_name, p.last_name, p.position, p.jersey_number "
			"ORDER BY p.position, p.last_name",
			(team[0],),
		)
		roster = pd.DataFrame(
			cursor.fetchall(),
			columns=["First Name", "Last Name", "Position", "Jersey Number", "Total Goals"],
		)
		st.dataframe(roster, hide_index=True, width="stretch")
	else:
		st.info("No teams found.")

elif page == "</>  SQL Query":
	st.header("🔍 SQL Query Explorer")

	sql_questions = [
		{
			"S.No": 1,
			"Question": "List all NHL teams alphabetically.",
			"Answer SQL Query": "SELECT team_name, team_abbrev FROM teams ORDER BY team_name;",
		},
		{
			"S.No": 2,
			"Question": "Count the total number of teams.",
			"Answer SQL Query": "SELECT COUNT(*) AS total_teams FROM teams;",
		},
		{
			"S.No": 3,
			"Question": "Show all players with their team names.",
			"Answer SQL Query": "SELECT CONCAT(p.first_name, ' ', p.last_name) AS player, t.team_name FROM players p JOIN teams t ON t.team_id = p.team_id ORDER BY player;",
		},
		{
			"S.No": 4,
			"Question": "Find the number of players at each position.",
			"Answer SQL Query": "SELECT position, COUNT(*) AS player_count FROM players GROUP BY position ORDER BY player_count DESC;",
		},
		{
			"S.No": 5,
			"Question": "Find the top 10 goal scorers for a selected season.",
			"Answer SQL Query": "SELECT CONCAT(p.first_name, ' ', p.last_name) AS player, s.goals FROM skater_stats s JOIN players p ON p.player_id = s.player_id WHERE s.season = '20242025' ORDER BY s.goals DESC LIMIT 10;",
		},
		{
			"S.No": 6,
			"Question": "Find the top 10 players by points for a selected season.",
			"Answer SQL Query": "SELECT CONCAT(p.first_name, ' ', p.last_name) AS player, s.points FROM skater_stats s JOIN players p ON p.player_id = s.player_id WHERE s.season = '20242025' ORDER BY s.points DESC LIMIT 10;",
		},
		{
			"S.No": 7,
			"Question": "Find the player with the most assists in all seasons.",
			"Answer SQL Query": "SELECT CONCAT(p.first_name, ' ', p.last_name) AS player, SUM(s.assists) AS total_assists FROM skater_stats s JOIN players p ON p.player_id = s.player_id GROUP BY p.player_id, p.first_name, p.last_name ORDER BY total_assists DESC LIMIT 1;",
		},
		{
			"S.No": 8,
			"Question": "Show the top five goalies by save percentage for a selected season.",
			"Answer SQL Query": "SELECT CONCAT(p.first_name, ' ', p.last_name) AS player, g.save_pct FROM goalie_season_stats g JOIN players p ON p.player_id = g.player_id WHERE g.season = '20242025' AND g.save_pct IS NOT NULL ORDER BY g.save_pct DESC LIMIT 5;",
		},
		{
			"S.No": 9,
			"Question": "Show teams ordered by wins for a selected season.",
			"Answer SQL Query": "SELECT t.team_name, s.wins FROM standings s JOIN teams t ON t.team_id = s.team_id WHERE s.season = '20252026' ORDER BY s.wins DESC;",
		},
		{
			"S.No": 10,
			"Question": "Show the top five teams by points for a selected season.",
			"Answer SQL Query": "SELECT t.team_name, s.points FROM standings s JOIN teams t ON t.team_id = s.team_id WHERE s.season = '20252026' ORDER BY s.points DESC LIMIT 5;",
		},
		{
			"S.No": 11,
			"Question": "Calculate total goals scored by each team in game statistics.",
			"Answer SQL Query": "SELECT t.team_name, SUM(gs.goals) AS total_goals FROM game_stats gs JOIN teams t ON t.team_id = gs.team_id GROUP BY t.team_id, t.team_name ORDER BY total_goals DESC;",
		},
		{
			"S.No": 12,
			"Question": "Count completed games by season.",
			"Answer SQL Query": "SELECT season, COUNT(*) AS completed_games FROM games WHERE game_state = 'FINAL' GROUP BY season ORDER BY season DESC;",
		},
		{
			"S.No": 13,
			"Question": "Find the highest-scoring completed game.",
			"Answer SQL Query": "SELECT game_id, game_date, home_score, away_score, home_score + away_score AS total_goals FROM games WHERE game_state = 'FINAL' ORDER BY total_goals DESC LIMIT 1;",
		},
		{
			"S.No": 14,
			"Question": "Show each team's home and away wins in the standings.",
			"Answer SQL Query": "SELECT t.team_name, s.home_wins, s.away_wins FROM standings s JOIN teams t ON t.team_id = s.team_id WHERE s.season = '20252026' ORDER BY t.team_name;",
		},
		{
			"S.No": 15,
			"Question": "Find players who scored at least 40 goals in a selected season.",
			"Answer SQL Query": "SELECT CONCAT(p.first_name, ' ', p.last_name) AS player, s.goals FROM skater_stats s JOIN players p ON p.player_id = s.player_id WHERE s.season = '20242025' AND s.goals >= 40 ORDER BY s.goals DESC;",
		},
	]

	
	query_options = [f"{q['S.No']}. {q['Question']}" for q in sql_questions]
	
	st.markdown("**Pick a ready-made query below, or choose Custom Query to write your own**")
	
	col1, col2 = st.columns([3, 1])
	with col1:
		selected_query = st.selectbox("Choose a query", query_options + ["Custom Query"], label_visibility="collapsed")
	
	st.markdown("**SQL Query**")
	
	if selected_query == "Custom Query":
		query_text = st.text_area("", value="", height=120, label_visibility="collapsed")
	else:
		# Get the selected question's query
		question_index = int(selected_query.split(".")[0]) - 1
		query_text = st.text_area("", value=sql_questions[question_index]["Answer SQL Query"], height=120, label_visibility="collapsed")
	
	if st.button("▶ Run Query"):
		try:
			cursor.execute(query_text)
			result_rows = cursor.fetchall()
			result_columns = [column[0] for column in cursor.description]
			
			
			st.success(f"✓ {len(result_rows)} rows returned")
			
			
			st.dataframe(
				pd.DataFrame(result_rows, columns=result_columns),
				hide_index=True,
				width="stretch",
			)
		except Exception as e:
			st.error(f"Error executing query: {str(e)}")

elif page == "▥  Leaderboards":
	st.header("📊 Leaderboards")

	cursor.execute(
		"SELECT season FROM skater_stats "
		"UNION SELECT season FROM goalie_season_stats "
		"UNION SELECT season FROM standings ORDER BY season DESC"
	)
	seasons = [row[0] for row in cursor.fetchall() if row[0]]
	selected_season = st.selectbox("Season", ["All Seasons"] + seasons)
	skater_season_filter = "" if selected_season == "All Seasons" else " WHERE s.season = %s"
	goalie_season_filter = "" if selected_season == "All Seasons" else " AND g.season = %s"
	standing_season_filter = "" if selected_season == "All Seasons" else " AND s.season = %s"
	season_params = () if selected_season == "All Seasons" else (selected_season,)

	goals_tab, assists_tab, points_tab, penalties_tab, shots_tab, saves_tab, goalie_wins_tab, wins_tab, team_points_tab = st.tabs([
		"📖 Goals",
		"🎯 Assists",
		"⭐ Points",
		"⏱ Penalty Minutes",
		"🏒 Shots",
		"🧤 Save %",
		"🥅 Goalie Wins",
		"🏆 Team Wins",
		"📌 Team Points",
	])

	with goals_tab:
		cursor.execute(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) AS Player, "
			"s.goals AS Goals "
			"FROM skater_stats s JOIN players p ON p.player_id = s.player_id "
			+ skater_season_filter + " ORDER BY s.goals DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Player", "Goals"]), hide_index=True, width="stretch")

	with assists_tab:
		cursor.execute(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) AS Player, "
			"s.assists AS Assists "
			"FROM skater_stats s JOIN players p ON p.player_id = s.player_id "
			+ skater_season_filter + " ORDER BY s.assists DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Player", "Assists"]), hide_index=True, width="stretch")

	with points_tab:
		cursor.execute(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) AS Player, "
			"s.points AS Points "
			"FROM skater_stats s JOIN players p ON p.player_id = s.player_id "
			+ skater_season_filter + " ORDER BY s.points DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Player", "Points"]), hide_index=True, width="stretch")

	with penalties_tab:
		cursor.execute(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) AS Player, "
			"s.penalty_min AS `Penalty Minutes` "
			"FROM skater_stats s JOIN players p ON p.player_id = s.player_id "
			+ skater_season_filter + " ORDER BY s.penalty_min DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Player", "Penalty Minutes"]), hide_index=True, width="stretch")

	with shots_tab:
		cursor.execute(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) AS Player, "
			"s.shots AS Shots "
			"FROM skater_stats s JOIN players p ON p.player_id = s.player_id "
			+ skater_season_filter + " ORDER BY s.shots DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Player", "Shots"]), hide_index=True, width="stretch")

	with saves_tab:
		cursor.execute(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) AS Player, "
			"g.save_pct AS save_pct_value "
			"FROM goalie_season_stats g JOIN players p ON p.player_id = g.player_id "
			"WHERE g.save_pct IS NOT NULL "
			+ goalie_season_filter + " ORDER BY g.save_pct DESC LIMIT 50",
			season_params,
		)
		st.dataframe(
			pd.DataFrame(cursor.fetchall(), columns=["Player", "Save %"]),
			hide_index=True,
			width="stretch",
		)

	with goalie_wins_tab:
		cursor.execute(
			"SELECT CONCAT(p.first_name, ' ', p.last_name) AS Player, "
			"g.wins AS Wins "
			"FROM goalie_season_stats g JOIN players p ON p.player_id = g.player_id "
			+ ("" if selected_season == "All Seasons" else " WHERE g.season = %s")
			+ " ORDER BY g.wins DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Player", "Wins"]), hide_index=True, width="stretch")

	with wins_tab:
		cursor.execute(
			"SELECT t.team_name AS Team, s.wins AS Wins "
			"FROM standings s JOIN teams t ON t.team_id = s.team_id "
			+ standing_season_filter + " ORDER BY s.wins DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Team", "Wins"]), hide_index=True, width="stretch")

	with team_points_tab:
		cursor.execute(
			"SELECT t.team_name AS Team, s.points AS Points "
			"FROM standings s JOIN teams t ON t.team_id = s.team_id "
			+ standing_season_filter + " ORDER BY s.points DESC LIMIT 50",
			season_params,
		)
		st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["Team", "Points"]), hide_index=True, width="stretch")

elif page == "⌕  Player Search":
	st.header("Player Search")

	cursor.execute(
		"SELECT player_id, first_name, last_name, position, headshot_url "
		"FROM players ORDER BY first_name, last_name"
	)
	players = cursor.fetchall()

	if players:
		player_labels = [
			f"{player[1]} {player[2]}" for player in players
		]
		selected_label = st.selectbox("Select Player", player_labels)
		selected_player = players[player_labels.index(selected_label)]

		photo, details = st.columns([1, 3])
		with photo:
			if selected_player[4]:
				st.image(selected_player[4], width=180)
		with details:
			st.subheader(f"{selected_player[1]} {selected_player[2]}")
			st.write(f"**Position:** {selected_player[3]}")

		cursor.execute(
			"SELECT CAST(COALESCE(SUM(goals), 0) AS UNSIGNED), "
			"CAST(COALESCE(SUM(assists), 0) AS UNSIGNED), "
			"CAST(COALESCE(SUM(points), 0) AS UNSIGNED), "
			"CAST(COALESCE(SUM(games_played), 0) AS UNSIGNED) "
			"FROM skater_stats WHERE player_id = %s",
			(selected_player[0],),
		)
		stats = cursor.fetchone()

		player_stats = [
			("Goals", stats[0]),
			("Assists", stats[1]),
			("Points", stats[2]),
			("Games Played", stats[3]),
		]
		for column, (label, value) in zip(st.columns(4), player_stats):
			column.metric(label, f"{value:,}")
	else:
		st.info("No players found.")

elif page == "⌁  Match Results":
	st.header("Match Results")

	cursor.execute("SELECT team_id, team_name, logo_url FROM teams ORDER BY team_name")
	teams = cursor.fetchall()

	if teams:
		team_names = [team[1] for team in teams]
		selected_name = st.selectbox("Select Team", team_names)
		selected_team = teams[team_names.index(selected_name)]

		logo, name = st.columns([1, 3])
		with logo:
			if selected_team[2]:
				st.image(selected_team[2], width=140)
		with name:
			st.subheader(selected_team[1])

		cursor.execute(
			"SELECT DISTINCT season FROM games "
			"WHERE home_team_id = %s OR away_team_id = %s "
			"ORDER BY season DESC",
			(selected_team[0], selected_team[0]),
		)
		seasons = [row[0] for row in cursor.fetchall() if row[0]]
		selected_season = st.selectbox("Season", ["All Seasons"] + seasons)
		season_filter = "" if selected_season == "All Seasons" else " AND season = %s"

		query = """
				SELECT game_date, venue_name, opponent, match_score, result
				FROM (
					SELECT
						g.game_date,
						g.season,
						g.venue_name,
						t.team_name AS opponent,
						CONCAT(g.home_score, ' - ', g.away_score) AS match_score,
						CASE
							WHEN g.home_score > g.away_score THEN 'W'
							WHEN g.home_score < g.away_score THEN 'L'
							ELSE 'T'
						END AS result
					FROM games g
					JOIN teams t ON t.team_id = g.away_team_id
					WHERE g.home_team_id = %s AND g.game_state = 'FINAL'

					UNION ALL

					SELECT
						g.game_date,
						g.season,
						g.venue_name,
						t.team_name AS opponent,
						CONCAT(g.away_score, ' - ', g.home_score) AS match_score,
						CASE
							WHEN g.away_score > g.home_score THEN 'W'
							WHEN g.away_score < g.home_score THEN 'L'
							ELSE 'T'
						END AS result
					FROM games g
					JOIN teams t ON t.team_id = g.home_team_id
					WHERE g.away_team_id = %s AND g.game_state = 'FINAL'
				) AS past_matches
				WHERE 1 = 1""" + season_filter + """
				ORDER BY game_date DESC
			"""
		params = (selected_team[0], selected_team[0])
		if selected_season != "All Seasons":
			params += (selected_season,)
		cursor.execute(query, params)
		matches = pd.DataFrame(
			cursor.fetchall(),
			columns=["Date", "Venue", "Opponent", "Match", "Result"],
		)

		st.dataframe(matches, hide_index=True, width="stretch")
	else:
		st.info("No teams found.")

