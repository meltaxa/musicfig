# Musicfig
<p/>
Make your LEGO Minifigures play music using a Raspberry Pi and a LEGO Dimensions toy pad.
<p align="center">
  <img src="https://cdn-images-1.medium.com/max/800/1*v3m7mg7Y_Vzy2y8O8gKXMQ.jpeg" alt="Musicfig rig"/>
</p>
<p/>
Leveraging the NFC chip in a LEGO Dimensions tag, Minifigues can be assigned songs and cue music like a jukebox.
<p/>
Jukebox control is not limited to LEGO minifigures. Disney Infinity characters, Amiibos, Skylanders, NFC tags, stickers or cards can become a Musicfig.
<p/>
During song play, the LEGO Dimensions pad will light up for the duration of the song.
<p/>
For Spotify users, the album art of the currently playing track is displayed on your local Musicfig app site, as demonstrated on the 
<a href="https://nowplaying.musicfig.com?github">https://nowplaying.musicfig.com</a> site: <p/>
<p align="center">
  <img src="https://musicfig.com/images/nowplaying.png?github" alt="Musicfig now playing" width=60%/><br>
Musicfig's now playing page.
</p>

# You will require

| Hardware | NFC tags |
| --- | --- |
| <img src="https://cdn-images-1.medium.com/max/400/1*CAcSKjlKsD9Ld-iuKsCY-Q.jpeg"><br><ul><li>Raspberry Pi with Python 3.8 installed.</li><li>LEGO Dimensions pad from either a PS3, PS4 or Wii game console. The Xbox version is not supported.</li></ul>| <img src="https://cdn-images-1.medium.com/max/400/1*UtAav5Iu2iOGxoS7a1nzTg.png"><br>From Lego Dimensions character discs, Disney Infinity character toys, NFC NTAG213 tags, stickers or cards. |

To play music you can use the following **options**:

* MP3 files;

* A Spotify Premium subscription account. For an enhanced experience, Spotify is recommended but not required.

# Install

* Complete installation instructions is available in the Medium article "[My LEGO Minifigures Play Spotify](https://medium.com/@mellican/my-lego-minifigures-play-spotify-dc397e83280e)".

# Quick Install (without Spotify)

This allows Musicfig to play in offline mode, by accessing local MP3 files. 

Firstly, connect your LEGO Dimensions toy pad to the Raspberry Pi via the USB port.

Now connect the speakers to the Raspberry Pi.

Follow these steps to install and config the Musicfig software:

* Install Python 3.8+.
* Clone this repository and run the install.sh script. Musicfig will start automatically.
* Copy your mp3 files to the music folder.
* Place your first tag on the pad and watch the system console log as the app discovers the UID value.
* Edit the tags.yml file with the UID and the mp3 file to be played.
* Place the tag off and on again. 
* A track should now start playing locally.

# Updating

* Re-run the install.sh script to pull down the latest code. 

# Everything is Awesome!
<p align="center">
  <img src="https://musicfig.com/images/1.jpg" width=50%>
</p>
Send feedback and photos of your Musicfigs and rigs over in the <a href="https://github.com/meltaxa/musicfig/discussions">Discussions</a>
section.
