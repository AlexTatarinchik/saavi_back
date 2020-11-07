docker build . -t saavi_back
docker run -d -p 5000:5000 saavi_back