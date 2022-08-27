#!/bin/bash

systemctl stop authlog_exporter.service
install_dir="/usr/local/lib/authlog_exporter"

pip install -r requirements.txt
mkdir $install_dir
cp authlog_exporter.py $install_dir
cp authlog_exporter.service $install_dir
chown root:root $install_dir/authlog_exporter.*
chmod 644 $install_dir/authlog_exporter.*
chmod o+x $install_dir/authlog_exporter.py
cp authlog_exporter.yml /etc/
chmod 644 /etc/authlog_exporter.yml
chown root:root /etc/authlog_exporter.yml


ln -sf $install_dir/authlog_exporter.service /etc/systemd/system/authlog_exporter.service
systemctl daemon-reload
systemctl enable authlog_exporter.service
systemctl start authlog_exporter.service




