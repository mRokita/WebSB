import ConfigParser
import os.path

class ConfigNotFound(Exception):
    pass

conf = ConfigParser.ConfigParser()
config_paths = ["sb.ini", "/etc/websb/sb.ini"]

config_path = None
for path in config_paths:
    if os.path.isfile(path):
        print "Loading config from {}.".format(path)
        config_path = path
        conf.read(path)
        break

if not config_path:
    raise ConfigNotFound("Couldn't find any config in ./sb.ini and /etc/websb/sb.ini")

database_uri = conf.get("Database", "uri")
timeout = float(conf.get("Connection", "timeout"))