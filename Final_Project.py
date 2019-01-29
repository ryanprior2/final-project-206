from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import unittest
import sqlite3
import matplotlib.pyplot as plt
import Spotify_Info
import csv
''' Lines 1-7 import all of the necessary modules. '''
client_credentials_manager = SpotifyClientCredentials(client_id=Spotify_Info.client_id, client_secret=Spotify_Info.client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
''' Lines 9-10 set up credentials to access the Spotify API through the Spotipy module and creates the session.
	https://spotipy.readthedocs.io/en/latest/ is the website that helped me learn Spotipy's formatting. '''
conn = sqlite3.connect('Songs.sqlite')
cur = conn.cursor()
conn_2 = sqlite3.connect('Songs_2.sqlite')
cur_2 = conn_2.cursor()	
conn_3 = sqlite3.connect('Songs_3.sqlite')
cur_3 = conn_3.cursor()
''' Lines 12-17 create cursors for three different SQLite tables that will correlate to three playlists. '''
def make_song_tables():
	data = sp.user_playlist_tracks('ryan.prior5',playlist_id='spotify:user:ryan.prior5:playlist:69v2WTRWAnOyBL8GRrXQpK',limit=100)
	items_1 = data['items']
	song_list = []
	for song in items_1:
		song_list.append((song['track']['name'],song['track']['popularity'],song['track']['album']['release_date']))
	cur.execute('DROP TABLE IF EXISTS Songs')
	cur.execute('CREATE TABLE Songs(song_name TEXT,popularity INTEGER,release_year INTEGER)')
	for song in song_list:
		cur.execute('INSERT INTO Songs(song_name,popularity,release_year) VALUES (?, ?, ?)', (song[0],song[1],song[2][0:4]))
		conn.commit()

	data_2 = sp.user_playlist_tracks('ryan.prior5',playlist_id='spotify:user:ryan.prior5:playlist:2xIvdaMd38BpbZQXcyystw',limit=100)
	items_2 = data_2['items']
	song_list_2 = []
	for song in items_2:
		song_list_2.append((song['track']['name'],song['track']['popularity'],song['track']['album']['release_date']))
	cur_2.execute('DROP TABLE IF EXISTS Songs_2')
	cur_2.execute('CREATE TABLE Songs_2(song_name TEXT,popularity INTEGER,release_year INTEGER)')
	for song in song_list_2:
		cur_2.execute('INSERT INTO Songs_2(song_name,popularity,release_year) VALUES (?, ?, ?)', (song[0],song[1],song[2][0:4]))
	conn_2.commit()

	data_3 = sp.user_playlist_tracks('ryan.prior5',playlist_id='spotify:user:ryan.prior5:playlist:7AodViA8xmWTL2sYfey1DZ',limit=100)
	items_3 = data_3['items']
	song_list_3 = []
	for song in items_3:
		song_list_3.append((song['track']['name'],song['track']['popularity'],song['track']['album']['release_date']))
	cur_3.execute('DROP TABLE IF EXISTS Songs_3')
	cur_3.execute('CREATE TABLE Songs_3(song_name TEXT,popularity INTEGER,release_year INTEGER)')
	for song in song_list_3:
		cur_3.execute('INSERT INTO Songs_3(song_name,popularity,release_year) VALUES (?, ?, ?)', (song[0],song[1],song[2][0:4]))
	conn_3.commit()
''' The function make_song_tables does not take an input and pulls the data from three Spotify playlists from 
	my account. 100 songs are pulled from each and the song names, popularity ranks, and release years are stored
	in their own SQLite tables. There is no output, it just caches the data into tables. '''
def calculate_popularity_decade(cur, cur_2, cur_3):
	tuple_list = []
	cur.execute('SELECT popularity, release_year from Songs')
	cur_2.execute('SELECT popularity, release_year from Songs_2')
	cur_3.execute('SELECT popularity, release_year from Songs_3')
	for song in cur:
		tuple_list.append((song[0], str(song[1])))
	for song in cur_2:
		tuple_list.append((song[0], str(song[1])))
	for song in cur_3:
		tuple_list.append((song[0], str(song[1])))
	
	decade_list = []
	for song in tuple_list:
		year = song[1]
		if year[3] != '0':
			year = year[0:3] + '0'
		if year not in decade_list:
			decade_list.append(year)
	decade_list.sort()
	
	popularity_list = []
	for decade in decade_list:
		total_popularity = 0
		counter = 0
		for song in tuple_list:
			if song[1][0:3] == decade[0:3]:
				total_popularity += song[0]
				counter += 1
		popularity_list.append(total_popularity/counter)
	
	decade_dict = {}
	for num in range(len(decade_list)):
		decade_dict[decade_list[num]] = popularity_list[num] 
	outfile =  open('decade_popularity.csv', 'w', newline = '')
	writer = csv.DictWriter(outfile, fieldnames = ['Decade', 'Average Song Popularity'])
	writer.writeheader()
	for decade in decade_dict:
	    writer.writerow({'Decade':decade, 'Average Song Popularity':decade_dict[decade]})
	outfile.close()

	return(decade_list, popularity_list)
''' The calculate_popularity_decade function takes the three SQLite data tables as inputs and then combines
	all of the songs into one list of tuples. The function is calculating the average popularity of songs per
	decade out of the whole 300. The return is two lists ready to be used for a graph that are in corresponding
	order, one with decades and the other with popularity average. As well, a CSV file is written with the new data. '''
def make_line_graph(calculations):
	decade_list = calculations[0]
	popularity_list = calculations[1]
	fig, ax = plt.subplots()
	ax.plot(decade_list, popularity_list, 'red', label = 'All Playlists')
	ax.set(xlabel='Decade', ylabel='Average Song Popularity', title='Average Popularity of Songs in Decade')
	ax.grid()
	fig.savefig("decade_popularity.png")
	plt.show()
''' The make_line_graph function takes the output calculations from the calculate_popularity_decade function
	as an input. There is no return value but the output is a line graph that shows when ran. The line graph
	displays the average song popularity by decade for all three playlists combined. '''
def calculate_playlist_ages(cur, cur_2, cur_3):
	cur.execute('SELECT release_year from Songs')
	song_list = []
	for song in cur:
		song_list.append(2018 - song[0])
	song_total = 0
	for song in song_list:
		song_total += song
	average_age = song_total/len(song_list)

	cur_2.execute('SELECT release_year from Songs_2')
	song_list_2 = []
	for song in cur_2:
		song_list_2.append(2018 - song[0])
	song_total_2 = 0
	for song in song_list_2:
		song_total_2 += song
	average_age_2 = song_total_2/len(song_list_2)

	cur_3.execute('SELECT release_year from Songs_3')
	song_list_3 = []
	for song in cur_3:
		song_list_3.append(2018 - song[0])
	song_total_3 = 0
	for song in song_list_3:
		song_total_3 += song
	average_age_3 = song_total_3/len(song_list_3)

	age_dict = {'Songs':average_age, 'Songs_2':average_age_2, 'Songs_3':average_age_3}
	outfile =  open('playlist_age.csv', 'w', newline = '')
	writer = csv.DictWriter(outfile, fieldnames = ['Playlist Table Name', 'Average Age of Songs'])
	writer.writeheader()
	for playlist in age_dict:
	    writer.writerow({'Playlist Table Name':playlist, 'Average Age of Songs':age_dict[playlist]})
	outfile.close()
	
	return[average_age, average_age_2, average_age_3]
''' The calculate_playlist_age function takes the three SQLite data tables as inputs and calculates the age, which
	is the average age of songs in the playlist, of each playlist. Those three values are the outputs. As well, 
	another CSV file is written with the new data. '''
def make_bar_chart(calculations):	
	average_age_list = calculations
	fig, ax = plt.subplots()
	p1 = ax.bar(1, average_age_list[0], .5, color='blue')
	p2 = ax.bar(1.5, average_age_list[1], .5, color='green')
	p3 = ax.bar(2, average_age_list[2], .5, color='orange')
	ax.set_xticks(range(1))
	ax.set(xlabel='Playlist - SQLite Table Name', ylabel='Average Age of Songs', title='Average Age of Songs in each Playlist')
	ax.grid()
	ax.legend((p1, p2, p3), ('Songs', 'Songs_2', 'Songs_3'))
	fig.savefig("average_age.png")
	plt.show()
''' The make_bar_chart function takes the output calculations from the calculate_playlist_age function as an
	input. It then makes a bar chart with the three values given for the three respective playlists. Again, there
	is no return value but the chart will be made when ran. '''
def run_all():
	make_song_tables()
	make_line_graph(calculate_popularity_decade(cur, cur_2, cur_3))
	make_bar_chart(calculate_playlist_ages(cur, cur_2, cur_3))
''' The run_all function simply calls all of the other functions correctly and in the right order. '''
run_all()
''' This runs the program. '''