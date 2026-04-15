# Show all
sudo docker ps -a

# Stop & Remove All Containers
sudo docker rm -f $(docker ps -aq)

# Start compose
sudo docker compose --env-file ../.env up -d