#! /bin/zsh
gnome-terminal -t "Server" -- bash -c "./server;exec bash;"
sleep 0.1
gnome-terminal -t "Analyse Pre HTML" -- bash -c "python3 analyse_pre_url.py;exec bash;"
sleep 0.1
gnome-terminal -t "Analyse User HTML" -- bash -c "python3 analyse_user_data.py;exec bash;"
sleep 0.1
gnome-terminal -t "Connect User URL" -- bash -c "python3 connect_user_url.py;exec bash;"
sleep 0.1
gnome-terminal -t "Connect Pre URL" -- bash -c "python3 connect_pre_url.py;exec bash;"
sleep 0.1
gnome-terminal -t "Analyse Pre HTML 2" -- bash -c "python3 analyse_pre_url_2.py;exec bash;"
sleep 0.1
gnome-terminal -t "Analyse User HTML 2" -- bash -c "python3 analyse_user_data_2.py;exec bash;"
sleep 0.1
gnome-terminal -t "Connect User URL 2" -- bash -c "python3 connect_user_url_2.py;exec bash;"
sleep 0.1
gnome-terminal -t "Connect Pre URL 2" -- bash -c "python3 connect_pre_url_2.py;exec bash;"
sleep 0.1
#gnome-terminal -t "Url Set" -- bash -c "python3 url_set.py;exec bash;"
