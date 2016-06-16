from urllib import urlopen
import re
from socket import socket, AF_INET, SOCK_DGRAM, timeout
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import reconstructor, relationship
from datetime import datetime
import config
Base = declarative_base()

PATTERN_SERVER = re.compile("(\d+\\.\d+\\.\d+\\.\d+):(\d+)")
PATTERN_VAR = re.compile("\\\\([^\\\\]+)\\\\([^\\\\]+)")
PATTERN_PLAYER = re.compile("(\d+) (\d+) \\\"(.*?)\\\"")
PATTERN_PCOLOR = re.compile("\\!(\d+)")

ESCAPE_TAB = ['\0', '-', '-', '-', '_', '*', 't', '.', 'N', '-', '\n', '#', '.', '>', '*', '*',
              '[', ']', '@', '@', '@', '@', '@', '@', '<', '>', '.', '-', '*', '-', '-', '-',
              ' ', '!', '\"', '#', '$', '%', '&', '\'','(', ')', '*', '+', ',', '-', '.', '/',
              '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
              '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
              'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_',
              '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
              'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', '<',
              '(', '=', ')', '^', '!', 'O', 'U', 'I', 'C', 'C', 'R', '#', '?', '>', '*', '*',
              '[', ']', '@', '@', '@', '@', '@', '@', '<', '>', '*', 'X', '*', '-', '-', '-',
              ' ', '!', '\"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/',
              '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
              '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
              'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_',
              '`', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
              'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '{', '|', '}', '~', '<']


class InvalidDataException(Exception):
    pass


class Player(Base):
    __tablename__ = "player"
    id = Column(Integer, autoincrement=True, primary_key=True)
    score = Column(Integer)
    ping = Column(Integer)
    name = Column(String(128))
    server_id = Column(Integer, ForeignKey('server.id'))
    def __init__(self, string):
        data = PATTERN_PLAYER.findall(string)
        if not data or len(data[0]) < 3:
            raise InvalidDataException("Couldn't parse {}".format(string))
        self.score, self.ping, self.name = (int(data[0][0]), int(data[0][1]), data[0][2])
        self.__escape_name()

    def __escape_name(self):
        """Replace special chars of ingame name."""
        name = ""
        skip_next = False
        for char in self.name:
            if skip_next:
                skip_next = False
                continue
            char_num = ord(char)
            if char_num == 136:  # color
                skip_next = True
                continue
            name += ESCAPE_TAB[ord(char)]
        self.name = name

    def __repr__(self):
        return "<Player({}, {}, {})>".format(self.score, self.ping, self.name)


class Variable(Base):
    __tablename__ = "variable"
    id = Column(Integer, autoincrement=True, primary_key=True)
    variable = Column(String(128))
    value = Column(String(128))
    server_id = Column(Integer, ForeignKey("server.id"))


class Server(Base):
    """Server info"""
    __tablename__ = "server"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String(128))
    port = Column(Integer)
    variables = relationship("Variable")
    players = relationship("Player")
    hostname = Column(String(256))
    mapname = Column(String(256))
    maxclients = Column(Integer)
    players_count = Column(Integer)
    scan_id = Column(Integer, ForeignKey("scan.id"))
    scan = relationship("Scan", foreign_keys = [scan_id])

    def __init__(self, ip, port):
        """Download server's status and init object."""
        self.port = port
        self.ip = ip
        conn = socket(AF_INET, SOCK_DGRAM)
        conn.settimeout(config.timeout)
        conn.sendto("\xFF\xFF\xFF\xFFstatus\0", (ip, port))
        data = conn.recv(4096)
        data_spl = data.split("\n")
        vars_str = data_spl[1]
        players_str = data_spl[2:]
        vars_data = dict([(match[0], match[1]) for match in PATTERN_VAR.findall(vars_str)])
        self.variables = list()
        for var in vars_data:
            self.variables.append(Variable(variable=var, value=vars_data[var]))
        self.players = list()
        for player_str in players_str:
            if player_str:
                self.players.append(Player(player_str))
        self.players_count = len(self.players)
        self.hostname = self.get_variable("hostname").value
        self.mapname = self.get_variable("mapname").value
        self.maxclients = self.get_variable("maxclients").value

    def to_dict(self, show_players, show_variables):
        sinfo = {"ip": str(self.ip),
                 "port": self.port,
                 "player_count": self.players_count,
                 "mapname": self.mapname,
                 "maxclients": self.maxclients,
                 "hostname": self.hostname}

        if show_variables:
            sinfo["variables"] = []
            for var in self.variables:
                sinfo["variables"].append({"variable": var.variable,
                                           "value": var.value})
        if show_players:
            var_to_color = {"po": "observer", "pr": "red", "pb": "blue", "pp": "purple", "py": "yellow"}
            teams = {}
            for cl in ["po", "pr", "py", "pb", "pp"]:
                v = self.get_variable(cl)
                if v:
                    pl = PATTERN_PCOLOR.findall(v.value)
                    for id in pl:
                        teams[int(id)] = var_to_color[cl]
            sinfo["players"] = [{"score": self.players[pnum].score,
                                 "ping": self.players[pnum].ping,
                                 "name": self.players[pnum].name,
                                 "team": teams[pnum] if pnum in teams else "connecting"}
                                 for pnum in range(len(self.players))]
        return sinfo

    def get_variable(self, name):
        for variable in self.variables:
            if variable.variable == name:
                return variable

    def __repr__(self):
        return "<Server ({}, {}:{}, {})>".format(self.get_variable("hostname").value, self.ip, self.port, len(self.players))


class Scan(Base):
    __tablename__ = "scan"
    id = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(DateTime, primary_key=True)
    servers = relationship("Server")

    def __init__(self, servers):
        self.time = datetime.now()
        self.servers = servers


class ServerBrowser:
    """This class is a container of server info."""
    def __init__(self, server_list_url="http://dplogin.com/serverlist.php"):
        """
        Initialize the object.

        :param server_list_url: location of the serverlist
        """
        self.__server_addr_list = list()
        self.__servers = list()
        self.__server_list_url = server_list_url

    def __load_servers(self):
        self.__servers = list()
        for server_addr in self.__server_addr_list:
            try:
                self.__servers.append(Server(*server_addr))
            except timeout:
                pass

    def __update_addr_list(self):
        """Update the list of server IPs."""
        self.__server_addr_list = list()
        conn = urlopen(self.__server_list_url)
        data = PATTERN_SERVER.findall(conn.readline())
        while data:
            self.__server_addr_list.append((data[0][0], int(data[0][1])))
            data = PATTERN_SERVER.findall(conn.readline())

    def get_scan(self):
        return Scan(self.__servers)

    def update(self):
        """Reload the serverlist."""
        self.__update_addr_list()
        self.__load_servers()

    @staticmethod
    def __create_server(ip, port):
        """Create an instance of Server."""
        return Server(ip, port)

    def add_server(self, ip, port):
        """Add a new server object to the serverlist."""
        self.__servers.append(self.__create_server(ip, port))

    def get_addr_list(self, update=True):
        """
        Get the list of server addrs.

        :param update: Perform an update of the list
        :return: list of server addrs
        """
        if update:
            self.__update_addr_list()
        return self.__server_addr_list
