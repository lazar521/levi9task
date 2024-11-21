from flask import request, jsonify
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    wins = db.Column(db.Integer, nullable=False, default=0)
    losses = db.Column(db.Integer, nullable=False, default=0)
    hoursPlayed = db.Column(db.Integer, nullable=False, default=0)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)
    ratingAdjustment = db.Column(db.Integer, nullable=True, default=0)
    elo = db.Column(db.Integer, nullable=True, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "wins": self.wins,
            "losses": self.losses,
            "hoursPlayed": self.hoursPlayed,
            "team_id": self.team_id,
            "ratingAdjustment": self.ratingAdjustment,
            "elo": self.elo,
        }


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamName = db.Column(db.String(80), unique=True, nullable=False)
    players = db.relationship("Player", backref="team", lazy=True)

    def to_dict(self):
        return {
            "teamName": self.teamName,
            "players": [player.to_dict() for player in self.players],
        }


# Create the database schema
with app.app_context():
    db.create_all()


# POST endpoint to add a new player
@app.route("/players/create", methods=["POST"])
def add_player():
    nickname = request.json.get("nickname")
    if not nickname:
        return jsonify({"error": "Nickname is required"}), 400

    if Player.query.filter_by(nickname=nickname).first():
        return jsonify({"error": "Nickname already exists"}), 400

    new_player = Player(nickname=nickname)
    db.session.add(new_player)
    db.session.commit()

    return (
        jsonify(new_player.to_dict()),
        201,
    )


@app.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    return jsonify(player.to_dict())


@app.route("/teams", methods=["POST"])
def add_team():
    teamName = request.json.get("teamName")
    playerIDs = request.json.get("players")

    if Team.query.filter_by(teamName=teamName).first():
        return jsonify({"error": "Team already exists"}), 400

    if not playerIDs or not teamName or len(playerIDs) != 5:
        return jsonify({"error": "Missing parameters"}), 400

    playerList = []
    for id in playerIDs:
        player = Player.query.filter_by(id=id).first()
        if not player:
            return jsonify({"error": f"Player {id} doesn't exist"}), 400
        if player.team_id is not None:
            return (
                jsonify({"error": f"Player {player.nickname} already has a team"}),
                400,
            )
        playerList.append(player)

    new_team = Team(teamName=teamName, players=playerList)
    db.session.add(new_team)
    db.session.commit()

    team = Team.query.filter_by(teamName=teamName).first()
    if team is None:
        return jsonify({}), 500

    for player in playerList:
        player.team_id = team.id

    db.session.commit()

    return jsonify(team.to_dict()), 200


@app.route("/teams/<int:team_id>", methods=["GET"])
def get_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    return jsonify(team.to_dict())


def updatePlayers(team, winnerId, duration, R2):
    if winnerId is None:
        win = 0
        loss = 0
        S = 0.5
    elif team.id == winnerId:
        win = 1
        loss = 0
        S = 1
    else:
        win = 0
        loss = 1
        S = 0

    for player in team.players:
        player.wins += win
        player.losses += loss
        player.hoursPlayed += duration

        if player.hoursPlayed < 500:
            player.ratingAdjustment = 50
        elif player.hoursPlayed < 1000:
            player.ratingAdjustment = 40
        elif player.hoursPlayed < 3000:
            player.ratingAdjustment = 30
        elif player.hoursPlayed < 5000:
            player.ratingAdjustment = 20
        else:
            player.ratingAdjustment = 10

        R1 = player.elo
        K = player.ratingAdjustment
        E = 1 / (1 + 10 ** ((R2 - R1) / 400))
        player.elo = round(R1 + K * (S - E))

    db.session.commit()


def avg_team_elo(team):
    sum = 0
    for player in team.players:
        sum += player.elo
    return sum // len(team.players)


@app.route("/matches", methods=["POST"])
def add_match():
    team1Id = request.json.get("team1Id")
    team2Id = request.json.get("team2Id")
    winningTeamId = request.json.get("winningTeamId")
    duration = request.json.get("duration")

    if winningTeamId != team1Id and winningTeamId != team2Id and winningTeamId != None:
        return jsonify({"error": "Incorrect winning team"}), 404

    team1 = Team.query.get(team1Id)
    team2 = Team.query.get(team2Id)

    if team1 is None or team2 is None:
        return jsonify({"error": "Team not found"}), 404

    updatePlayers(team1, winningTeamId, duration, avg_team_elo(team2))
    updatePlayers(team2, winningTeamId, duration, avg_team_elo(team1))

    return jsonify({}), 200


if __name__ == "__main__":
    app.run(port=8080)
