# Jukebox Portal

Listen to songs, albums or playlists by placing a LEGO minifigure on the 
LEGO Dimensions pad and enjoy the audio and light show!
<p align="center">
  <img src="https://cdn-images-1.medium.com/max/800/1*v3m7mg7Y_Vzy2y8O8gKXMQ.jpeg" alt="Jukebox Portal close up"/>
</p>
The "toys-to-life" LEGO Dimensions console game was discontinued in October 2017. 
Now you can bring it back to life as a Raspberry Pi jukebox by connecting the USB 
toy pad to a Raspberry Pi and running this Jukebox Portal app.
<p/>
<p/>
Jukebox control is not limited to LEGO minifigures. Disney Infinity 
characters, Amiibos, Skylanders, NFC tags, stickers or cards can be assigned to a Spotify song, 
album or playlist too.

While the light show plays for the duration of the track, on the Jukebox Portal 
web app, the album art of the current track is displayed when associated to a Spotify account. 
<p align="center">
  <img src="https://cdn-images-1.medium.com/max/640/1*A4Dv2PbAeniEmNKmR2469g.png" alt="Jukebox Portal screen shot"/>
</p>

# You will require

| Hardware | NFC tags |
| --- | --- |
| <img src="https://cdn-images-1.medium.com/max/400/1*CAcSKjlKsD9Ld-iuKsCY-Q.jpeg"><br><ul><li>Raspberry Pi with Python 3.8 installed.</li><li>LEGO Dimensions pad from either a PS3, PS4 or Wii game console. The Xbox version is not supported.</li></ul>| <img src="https://cdn-images-1.medium.com/max/400/1*UtAav5Iu2iOGxoS7a1nzTg.png"><br>From Lego Dimensions character discs, Disney Infinity character toys, NFC NTAG213 tags, stickers or cards. |

To play music you can use the following **options**:

* A Spotify Premium subscription account. For an enhanced experience, Spotify is recommended but not required.

* MP3 files. 

# Install

* Complete installation instructions is available in the Medium article "[My LEGO Minifigures Play Spotify](https://medium.com/@mellican/my-lego-minifigures-play-spotify-dc397e83280e)".

# Quick Install (without Spotify)

* Install Python 3.8+.
* Clone this repository and run the install.sh script.
* Copy your mp3 files to the music folder.
* Execute the Jukebox Portal run.py script.
* Place your first tag on the pad and watch the console log as the app discovers the UID value.
* Edit the tags.yml file accordingly with the aforementioned UID and mp3 file to be played.
* Place the tag off and on again. 
* A track should now start playing locally.

# Updating

* Pull the latest code from the repository and run the install.sh script.
