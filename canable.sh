sudo slcand -o -s8 -t hw -S 1000000 /dev/ttyACM5 can1
sudo ip link set can1 up
sudo ip link set can1 txqueuelen 1000
