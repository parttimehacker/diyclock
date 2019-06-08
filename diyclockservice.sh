sudo cp diyclock.service /lib/systemd/system/diyclock.service
sudo chmod 644 /lib/systemd/system/diyclock.service
sudo systemctl daemon-reload
sudo systemctl enable diyclock.service

