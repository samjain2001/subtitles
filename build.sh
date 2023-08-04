echo "imagemagick" >> ~/apt.txt
echo "imagemagick" >> /etc/environment
pip install -r requirements.txt
apt-get update
apt-get install -y imagemagick
pip install --upgrade moviepy
pip install Flask
pip show Flask
ffmpeg -version


