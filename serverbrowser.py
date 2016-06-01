from urllib import urlopen
import re
from socket import socket, AF_INET, SOCK_DGRAM, timeout


PATTERN_SERVER = re.compile("(\d+\\.\d+\\.\d+\\.\d+):(\d+)")
PATTERN_VAR = re.compile("\\\\([^\\\\]+)\\\\([^\\\\]+)")
PATTERN_PLAYER = re.compile("(\d+) (\d+) \\\"(.*?)\\\"")

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


class Player:
    def __init__(self, string):
        data = PATTERN_PLAYER.findall(string)
        if not data or len(data[0]) < 3:
            raise InvalidDataException("Couldn't parse {}".format(string))
        self.score, self.ping, self.name = data[0]
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


class Server:
    """Server info"""
    def __init__(self, ip, port):
        """Download server's status and init object."""
        self.port = port
        self.ip = ip
        conn = socket(AF_INET, SOCK_DGRAM)
        conn.settimeout(2)
        conn.sendto("\xFF\xFF\xFF\xFFstatus\0", (ip, port))
        data = conn.recv(4096)
        data_spl = data.split("\n")
        vars_str = data_spl[1]
        players_str = data_spl[2:]
        self.vars = dict([(match[0], match[1]) for match in PATTERN_VAR.findall(vars_str)])
        self.players = list()
        for player_str in players_str:
            if player_str:
                self.players.append(Player(player_str))

    def __repr__(self):
        return "<Server ({}, {}:{}, {})>".format(self.vars["hostname"], self.ip, self.port, len(self.players))


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
                print
                pass

    def __update_addr_list(self):
        """Update the list of server IPs."""
        self.__server_addr_list = list()
        conn = urlopen(self.__server_list_url)
        data = PATTERN_SERVER.findall(conn.readline())
        while data:
            self.__server_addr_list.append((data[0][0], int(data[0][1])))
            data = PATTERN_SERVER.findall(conn.readline())

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
