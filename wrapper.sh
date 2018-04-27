echo "-- STARTING --"
sleep 2
echo "- Play chord now..."
sleep 2

arecord -D plughw:1 -d 1 -t wav -r 44100 -f S16_LE input.wav
python run.py
rm -f input.wav

echo ""
echo ""
