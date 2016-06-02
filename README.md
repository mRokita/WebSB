# WebSB
A Web server browser for DP2 (http://digitalpaint.org)

# Instalation
```sh
git clone https://github.com/mRokita/WebSB
cd WebSB
sudo python setup.py install
```

# Configuration
- Create a SQL database (and user) for WebSB
- Edit the config
```sh
cd /etc/websb/
cp sb.default.ini sb.ini
edit sb.ini # Specify the URI of that database in this file
```
- Add the website to apache2's site config (the defaut location is /etc/apache2/sites-enabled/000-default.conf)
```
WSGIScriptAlias / /usr/share/websb/webserverbrowsers.wsgi
```
- Restart apache2
```
service apache2 start
```
# Running
```sh
sudo /etc/init.d/websbd start # Or sudo service websbd start
```
