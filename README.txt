NHL Hockey Analytics Dashboard
==============================

What this project does
----------------------
This project loads NHL data into a MySQL database and shows the data in a Streamlit dashboard.

Main pages
----------
1. Home
   Shows the NHL dashboard title, a hockey image, and four summary sections:
   - Total Teams: Number of teams in the database.
   - Total Players: Number of players in the database.
   - Total Games: Number of unique games in the game statistics table.
   - Total Goals: Total goals in the game statistics table.
   It also shows the top scorer, best goal saver, league leader team, and player with the most assists.

2. Standings
   Shows team standings in a table. The table includes team logo, team name, conference, division, games played, wins, losses, overtime losses, points, goals for, goals against, home wins, and away wins.
   Use the Conference and Division selectors to filter the table. Use Team Filter and the rank slider to show a selected rank range.

3. Team Info
   Select a team to view its logo, name, abbreviation, conference, division, and current standing.
   The roster table shows each player's first name, last name, position, jersey number, and total goals.

4. Player Search
   Select a player to view the player's headshot, name, and position.
   The page also shows total goals, assists, points, and games played from the skater statistics table.

5. Match Results
   Select a team to view its completed games. Select a season or All Seasons to filter the results.
   The table shows game date, venue, opponent, score, and result. Results are shown from the selected team's point of view as W, L, or T.

6. Leaderboards
   Select a season or All Seasons. Use the tabs to view:
   - Goals
   - Assists
   - Points
   - Penalty Minutes
   - Shots
   - Save Percentage
   - Goalie Wins
   - Team Wins
   - Team Points
   Player and team results are sorted from highest to lowest where appropriate.

7. SQL Query
   Shows 15 SQL practice questions. Expand a question to display its answer data in a table below the question.
   The SQL statements are hidden on the app page. The answer data is loaded from the NHL database.

Project files
-------------
- app.py: Streamlit dashboard application.
- NHL_Project.ipynb: Notebook used to load and inspect NHL data.
- sql_queries_notebook.txt: SQL queries used in the NHL_Project notebook.
- sql_queries_app.txt: SQL queries used in the Streamlit app.
- sql_practice_questions.txt: The 15 SQL practice questions and their answer queries.
- game_stats.json: Game statistics data.
- skater_season_stats.json: Skater season statistics data.
- goalie_season_stats.json: Goalie season statistics data.

Database requirements
---------------------
- MySQL must be running on localhost.
- Database name: nhl_project.
- MySQL user: ****.
- Password ****.
- The database should contain teams, players, games, game_stats, skater_stats, goalie_season_stats, and standings tables.

How to run the dashboard
------------------------
1. Open a terminal in the NHL_Project folder.
2. Install the required packages:
   pip install streamlit pandas pymysql sqlalchemy requests
3. Start the app:
   streamlit run app.py
4. Open the local URL shown by Streamlit.

How to use the SQL Query page
-----------------------------
Open SQL Query from the sidebar. Expand any numbered question. The answer appears as a data table below that question. 




