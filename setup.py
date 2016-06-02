# -*- coding: utf-8 -*-
from distutils.core import setup
from subprocess import call

call(["chmod", "+x", "websbd", "-v"])

setup(name="WebSB",
      version="1.0",
      description="Web server browser for Digital Paint: Paintball 2",
      author="Michał 'mRokita' Rokita",
      keywords=["sb", "server", "browser", "paintball", "paint", "digital", "dp"],
      author_email="mrokita+sb@mrokita.pl",
      packages=["websb"],
      scripts=["webserverbrowser"],
      requires=["sqlalchemy", "flask", "flask_sqlalchemy"],
      data_files=[('/etc/websb/', ['sb.default.ini']),
                  ('/usr/share/websb/', ['webserverbrowser.wsgi']),
                  ('/etc/init.d/', ['websbd'])]
      )