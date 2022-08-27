#!/bin/bash

install_dir="/usr/local/lib/authlog_exporter"

systemctl stop authlog_exporter.service
systemctl disable authlog_exporter.service
# rm /etc/systemd/system/authlog_exporter.service
systemctl daemon-reload

rm -rf $install_dir
rm /etc/authlog_exporter.yml