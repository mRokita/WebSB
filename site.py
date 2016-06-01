from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, and_
from sqlalchemy.sql.expression import func
from serverbrowser import Scan, Server, Player, Variable, Base
from config import database_uri
from json import dumps
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db = SQLAlchemy(app)

def get_show_args():
    return "show_variables" in request.args and request.args["show_variables"] == "1",\
           "show_players" in request.args and request.args["show_players"] == "1"

@app.route("/api/v1/scans/")
def get_scans():
    scans = list(db.session.query(Scan).order_by(Scan.time).all())
    data = dict()
    data["scans"] = [{"time": str(scan.time),
                      "id": scan.id,
                      "server_count": len(scan.servers),
                      "player_count": sum(server.players_count for server in scan.servers)} for scan in scans]
    return Response(dumps(data, indent=4), mimetype="text/json")

@app.route("/api/v1/scans/<id>/")
def get_scan(id):
    show_variables, show_players = get_show_args()
    if id == "latest":
        id = db.session.query(func.max(Scan.id)).first()[0]
    servers = db.session.query(Server).filter(Server.scan_id == id).order_by(desc(Server.players_count)).all()
    data = dict()
    data["id"] = id
    data["time"] = str(db.session.query(Scan).first().time)
    data["servers"] = []
    for server in sorted(servers, key=lambda s: -s.players_count):
        data["servers"].append(server.to_dict(show_players=show_players, show_variables=show_variables))
    return Response(dumps(data, indent=4), mimetype="text/json")

@app.route("/api/v1/scans/<id>/<ip>:<port>")
def get_server(id, ip, port):
    if id == "latest":
        id = db.session.query(func.max(Scan.id))
    show_variables, show_players = get_show_args()
    server = db.session.query(Server)\
        .filter(and_(Server.scan_id == id, Server.ip == ip,Server.port == port))\
        .first()
    sinfo = server.to_dict(show_players=show_players, show_variables=show_variables)
    return Response(dumps(sinfo, indent=4), mimetype="text/json")

if __name__ == "__main__":
    app.run(debug=True)