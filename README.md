# ChordApp
#### Video Demo:  <https://youtu.be/4nYh3hIxYcc>


# General description:
ChordApp is a web application that uses Python (with Flask), SQL, HTML (with Jinja), CSS (with Bootstrap) and JavaScript.
It's an application where users can transcribe songs with lyrics and chords so they and other users can play them with an instrument.

It is a community centered and moderated system, where users are the ones who create the songs and users are the ones who rate the songs, which means if someone creates a "troll" song with unuseful content, other users will rate it low and the song will be at the bottom of the list. 


## File by file explanation
### App.py:
Contains all of the routes and the backend logic of the application. 

### Helpers.py:
Contains the "login required" function which helps to make certain routes only accessible to logged users, and it also contains the "parse_content" function which takes the raw content the user inputs and converts the chords to be colored. 

### Styles.css:
Contains all of the CSS code of the application.

### Chordapp.db:
It's the application's database. Here's a list of its tables:
- Users. Contains all users of the application. 
- Artists. Contains all artists who own the songs.
- Genres. Contains all genres. 
- Songs. Contains a unique list of all the songs. 
- Versions. Contains all versions of a song. 

### Layout.html:
Contains the base layout for the application, which is the navbar, linking bootstrap and css to the html and initializing every html file that will be used. 

### Index.html:
In this case, this file is left for future delopment, when the app has enough content to have a main panel for the user to see, with their favorite songs and history of songs viewed, for example. Right not, songs.html is working as a homepage. 

### Songs.html:
Shows a table with a list of all the songs that exist in the app. Every row of the table is clickable and will take the user to the list of all versions for that song. In this page, the user can also press a button to create a new song, which will take them to the "add_song" page.  

### Song.html:
Contains a table that shows all of the existing versions for that song. The user can access any of them and can edit or delete any version they created. They can also press a button that will take them to the workstation where they can create their own version of the song. 

### Version.html:
Shows the song with its parsed and formatted content, with chords on top of the lyrics with a different color for easier recognition. It also contains the rating module at the bottom for users to rate the version on a scale from 1 to 5. 

### Workstation.html:
This is the page users will access to create a song from scratch or edit a song they already created at some point. It contains the instructions to write the songs and a textarea to write them. It also contains a "save version" button. 


### Add_song.html:
This is the page where a user can create a new song. They need to type the title, artist and genre of the song and submit it. This creates the song and redirects them to the song.html page, where they can now create the first version of the song. 

### Register.html:
It's the page where users can register, create a username, password and confirm the password. 

### Login.html:
It's the page where users login. 


## Use of AI:
I used AI for my project mostly for "macro-guideance" purposes, meaning I asked what to start with, what to follow with, what tables I needed in my database for what I wanted to create, etc. I used it mostly for working in an organized way and to have a well-made plan before actually starting to write code. 

In coding, I mostly tried to use my own code and asked AI to help me when it didn't work or asked it why it didn't work. 
Every moment I used AI, I always made sure to understand what it did so that I can learn instead of just letting it code for me. 

### AI agents used: 
- ChatGPT
- GitHub Copilot
- Grok