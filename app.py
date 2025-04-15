#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
#from flask_wtf import FlaskForm  (not used here but in forms.py)
from forms import *
from flask_migrate import Migrate

from datetime import datetime
import re
from operator import itemgetter # for sorting lists of tuples

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

# Initial population of the Genre table here --> No, for grading they want it to be blank
# (just the schema is defined) and we count on the web form validators to only show valid choices (forms.py)

# Association tables for Artist to Genre (many2many) and Venue to Genre (many2many)
# DEFINE the Genre table as the child since it normally doesn't matter which we pick, but in this case,
# its common to both many2many relationships and we have to constrain the parents to just one backref!
artist_genre_table = db.Table('artist_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True)
)

venue_genre_table = db.Table('venue_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True)
)


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))



    # Here we link the associative table for the m2m relationship with genre
    genres = db.relationship('Genre', 
                          secondary=venue_genre_table,
                          backref=db.backref('venues', lazy='dynamic'),
                          lazy='dynamic')
    # secondary links this to the associative (m2m) table name
    # can refences like venue.genres with the above statement
    # backref creates an attribute on Venue objects so we can also reference like: genre.venues

    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    # Venue is the parent (one-to-many) of a Show (Artist is also a foreign key, in def. of Show)
    # In the parent is where we put the db.relationship in SQLAlchemy
    shows = db.relationship('Show', backref='venue', lazy=True)    # Can reference show.venue (as well as venue.shows)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # Genre should be its own table, with a many2many relationship with Artist
    # and another many2many relationship with Venue
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # Here we link the associative table for the m2m relationship with genre
    genres = db.relationship('Genre', secondary=artist_genre_table, backref=db.backref('artists'))
    # secondary links this to the associative (m2m) table name
    # can refences like artist.genres with the above statement
    # backref creates an attribute on Artist objects so we can also reference like: genre.artists

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    # Artist is the parent (one-to-many) of a Show (Venue is also a foreign key, in def. of Show)
    # In the parent is where we put the db.relationship in SQLAlchemy
    shows = db.relationship('Show', backref='artist', lazy=True)    # Can reference show.artist (as well as artist.shows)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)    # Start time required field

    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)   # Foreign key is the tablename.pk
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} Artist={self.artist_id} Venue={self.venue_id}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')

@app.route('/test')
def test_route():
    return jsonify({'status': 'success', 'message': 'Test route working'})

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.all()  # Directly query the database for venues

    # Create a set of all the cities/states combinations uniquely
    cities_states = set()
    for venue in venues:
        cities_states.add((venue.city, venue.state))  # Add tuple

    # Turn the set into an ordered list
    cities_states = list(cities_states)
    cities_states.sort(key=itemgetter(1, 0))  # Sorts on second column first (state), then by city.

    now = datetime.now()  # Don't get this over and over in a loop!

    data = []  # Initialize data list before using it

    # Now iterate over the unique values to seed the data dictionary with city/state locations
    for loc in cities_states:
        venues_list = []
        for venue in venues:
            if (venue.city == loc[0]) and (venue.state == loc[1]):
                # Get all shows for this venue
                venue_shows = Show.query.filter_by(venue_id=venue.id).all()
                num_upcoming = sum(show.start_time > now for show in venue_shows)

                venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming
                })

        # After all venues are added to the list for a given location, add it to the data dictionary
        data.append({
            "city": loc[0],
            "state": loc[1],
            "venues": venues_list
        })

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '').strip()

    # Use filter, not filter_by when doing LIKE search (i=insensitive to case)
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()   # Wildcards search before and after
    #print(venues)
    venue_list = []
    now = datetime.now()
    for venue in venues:
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
        num_upcoming = 0
        for show in venue_shows:
            if show.start_time > now:
                num_upcoming += 1

        venue_list.append({
            "id": venue.id,
            "name": venue.name,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "image_link": venue.image_link,
            "genres": [genre.name for genre in venue.genres],
            "num_upcoming_shows": num_upcoming
        })


    if not venues:
        response = {
            "count": 0,
            "data": []
        }
    else:
        response = {
            "count": len(venue_list),
            "data": venue_list
        }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    print(f"Requested venue_id: {venue_id}")
    
    # First try to get venue from database
    venue = Venue.query.get(venue_id)
    
    if not venue:
        flash('Venue not found.')
        return redirect(url_for('index'))
    
    # Prepare venue data from database
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": [genre.name for genre in venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent if venue.seeking_talent is not None else False,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }

    # Get shows for this venue
    now = datetime.now()
    shows = Show.query.filter_by(venue_id=venue.id).order_by(Show.start_time).all()
    for show in shows:
        show_info = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
            
        if show.start_time > now:
            data["upcoming_shows"].append(show_info)
            data["upcoming_shows_count"] += 1
        else:
            data["past_shows"].append(show_info)
            data["past_shows_count"] += 1
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    address = form.address.data.strip()
    phone = form.phone.data
    # Normalize DB.  Strip anything from phone that isn't a number
    phone = re.sub(r'\D', '', phone) if phone else phone # e.g. (819) 392-1234 --> 8193921234
    genres = form.genres.data                   # ['Alternative', 'Classical', 'Country']
    seeking_talent = True if form.seeking_talent.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website_link.data.strip()
    facebook_link = form.facebook_link.data.strip()
    
    # Redirect back to form if errors in form validation
    if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_venue_form'))

    else:
        error_in_insert = False

        # Insert form data into DB
        try:
            # creates the new venue with all fields but not genre yet
            new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, \
                seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
                website=website, facebook_link=facebook_link)
            # genres can't take a list of strings, it needs to be assigned to db objects
            # genres from the form is like: ['Alternative', 'Classical', 'Country']
            for genre in genres:
                # fetch_genre = session.query(Genre).filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                fetch_genre = Genre.query.filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                if fetch_genre:
                    # if found a genre, append it to the list
                    new_venue.genres.append(fetch_genre)

                else:
                    # fetch_genre was None. It's not created yet, so create it
                    new_genre = Genre(name=genre)
                    db.session.add(new_genre)
                    new_venue.genres.append(new_genre)  # Create a new Genre item and append it

            db.session.add(new_venue)
            db.session.commit()
        except Exception as e:
            error_in_insert = True
            print(f'Exception "{e}" in create_venue_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_insert:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('index'))
        else:
            flash('An error occurred. Venue ' + name + ' could not be listed.')
            print("Error in create_venue_submission()")
            # return redirect(url_for('create_venue_submission'))
            abort(500)


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    # Deletes a venue based on AJAX call from the venue page
    venue = Venue.query.get(venue_id)
    if not venue:
        # User somehow faked this call, redirect home
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        # Need to hang on to venue name since will be lost after delete
        venue_name = venue.name
        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting venue {venue_name}.')
            print("Error in delete_venue()")
            abort(500)
        else:
            # flash(f'Successfully removed venue {venue_name}')
            # return redirect(url_for('venues'))
            return jsonify({
                'deleted': True,
                'url': url_for('venues')
            })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.order_by(Artist.name).all()  # Sort alphabetically

    data = []  # Initialize data list before using it

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Most of code is from search_venues()
    search_term = request.form.get('search_term', '').strip()

    # Use filter, not filter_by when doing LIKE search (i=insensitive to case)
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()   # Wildcards search before and after
    #print(artists)
    artist_list = []
    now = datetime.now()
    for artist in artists:
        artist_shows = Show.query.filter_by(artist_id=artist.id).all()
        num_upcoming = 0
        for show in artist_shows:
            if show.start_time > now:
                num_upcoming += 1

        artist_list.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming  # FYI, template does nothing with this
        })
    if not artists:
        response = {
            "count": 0,
            "data": []
        }
    else:
        response = {
        "count": len(artist_list),
        "data": artist_list
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Get artist by ID from database
    print(f"Requested venue_id: {artist_id}")
    artist = Artist.query.get(artist_id)
    
    if not artist:
        flash('Artist not found.')
        return redirect(url_for('index'))
        # For non-test artists, use database values
    data = {
            "id": artist.id,
            "name": artist.name,
            "genres": [genre.name for genre in artist.genres],  # Extract genre names from the InstrumentedList
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": [],
            "upcoming_shows": [],
            "past_shows_count": 0,
            "upcoming_shows_count": 0,
        }

    
        

    # Get shows for this artist
    now = datetime.now()
    shows = Show.query.filter_by(artist_id=artist.id).order_by(Show.start_time).all()
    for show in artist.shows:
        show_info = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        
        if show.start_time > now:
            data["upcoming_shows"].append(show_info)
            data["upcoming_shows_count"] += 1
        else:
            data["past_shows"].append(show_info)
            data["past_shows_count"] += 1
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # Taken mostly from edit_venue()

    # Get the existing artist from the database
    artist = Artist.query.get(artist_id)  # Returns object based on primary key, or None.  Guessing get is faster than filter_by
    if not artist:
        # User typed in a URL that doesn't exist, redirect home
        return redirect(url_for('index'))
    else:
        # Otherwise, valid artist.  We can prepopulate the form with existing data like this.
        # Prepopulate the form with the current values.  This is only used by template rendering!
        form = ArtistForm(obj=artist)

    # genres needs to be a list of genre strings for the template
    genres = [ genre.name for genre in artist.genres ]
    
    
    artist = {
        "id": artist_id,
        "name": artist.name,
        "genres": genres,
        # "address": artist.address,
        "city": artist.city,
        "state": artist.state,
    # Put the dashes back into phone number
    "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]) if len(artist.phone) == 10 else artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Much of this code from edit_venue_submission()
    form = ArtistForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    # address = form.address.data.strip()
    phone = form.phone.data
    # Normalize DB.  Strip anything from phone that isn't a number
    phone = re.sub(r'\D', '', phone) if phone else phone # e.g. (819) 392-1234 --> 8193921234
    genres = form.genres.data                   # ['Alternative', 'Classical', 'Country']
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website.data.strip()
    facebook_link = form.facebook_link.data.strip()
    
    # Redirect back to form if errors in form validation
    if not form.validate():
        flash( form.errors )
        return redirect(url_for('edit_artist', artist_id=artist_id))

    else:
        error_in_update = False

        # Insert form data into DB
        try:
            # First get the existing artist object
            artist = Artist.query.get(artist_id)
            # artist = Artist.query.filter_by(id=artist_id).one_or_none()

            # Update fields
            artist.name = name
            artist.city = city
            artist.state = state
            # artist.address = address
            artist.phone = phone

            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description
            artist.image_link = image_link
            artist.website = website
            artist.facebook_link = facebook_link

            # First we need to clear (delete) all the existing genres off the artist otherwise it just adds them
            
            # For some reason this didn't work! Probably has to do with flushing/lazy, etc.
            # for genre in artist.genres:
            #     artist.genres.remove(genre)
                        
            # artist.genres.clear()  # Either of these work.
            artist.genres = []
            
            # genres can't take a list of strings, it needs to be assigned to db objects
            # genres from the form is like: ['Alternative', 'Classical', 'Country']
            for genre in genres:
                fetch_genre = Genre.query.filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                if fetch_genre:
                    # if found a genre, append it to the list
                    artist.genres.append(fetch_genre)

                else:
                    # fetch_genre was None. It's not created yet, so create it
                    new_genre = Genre(name=genre)
                    db.session.add(new_genre)
                    artist.genres.append(new_genre)  # Create a new Genre item and append it

            # Attempt to save everything
            db.session.commit()
        except Exception as e:
            error_in_update = True
            print(f'Exception "{e}" in edit_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_update:
            # on successful db update, flash success
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash('An error occurred. Artist ' + name + ' could not be updated.')
            print("Error in edit_artist_submission()")
            abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # Get the existing venue from the database
    # venue = Venue.query.filter_by(id=venue_id).one_or_none()    # Returns one, None, or exception if more than one
    venue = Venue.query.get(venue_id)  # Returns object based on primary key, or None.  Guessing get is faster than filter_by
    if not venue:
        # User typed in a URL that doesn't exist, redirect home
        return redirect(url_for('index'))
    else:
        # Otherwise, valid venue.  We can prepopulate the form with existing data like this:
        form = VenueForm(obj=venue)

    # Prepopulate the form with the current values.  This is only used by template rendering!
    
    # genres needs to be a list of genre strings for the template
    genres = [ genre.name for genre in venue.genres ]
    
    

    venue = {
        "id": venue_id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
    # Put the dashes back into phone number
    "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]) if len(venue.phone) == 10 else venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Much of this code same as /venue/create view.
    form = VenueForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    address = form.address.data.strip()
    phone = form.phone.data
    # Normalize DB.  Strip anything from phone that isn't a number
    phone = re.sub(r'\D', '', phone) # e.g. (819) 392-1234 --> 8193921234
    genres = form.genres.data                   # ['Alternative', 'Classical', 'Country']
    seeking_talent = True if form.seeking_talent.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website.data.strip()
    facebook_link = form.facebook_link.data.strip()
    
    # Redirect back to form if errors in form validation
    if not form.validate():
        flash( form.errors )
        return redirect(url_for('edit_venue', venue_id=venue_id))

    else:
        error_in_update = False

        # Insert form data into DB
        try:
            # First get the existing venue object
            venue = Venue.query.get(venue_id)
            # venue = Venue.query.filter_by(id=venue_id).one_or_none()

            # Update fields
            venue.name = name
            venue.city = city
            venue.state = state
            venue.address = address
            venue.phone = phone

            venue.seeking_talent = seeking_talent
            venue.seeking_description = seeking_description
            venue.image_link = image_link
            venue.website = website
            venue.facebook_link = facebook_link

            # First we need to clear (delete) all the existing genres off the venue otherwise it just adds them
            
            # For some reason this didn't work! Probably has to do with flushing/lazy, etc.
            # for genre in venue.genres:
            #     venue.genres.remove(genre)
                        
            # venue.genres.clear()  # Either of these work.
            venue.genres = []
            
            # genres can't take a list of strings, it needs to be assigned to db objects
            # genres from the form is like: ['Alternative', 'Classical', 'Country']
            for genre in genres:
                fetch_genre = Genre.query.filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                if fetch_genre:
                    # if found a genre, append it to the list
                    venue.genres.append(fetch_genre)

                else:
                    # fetch_genre was None. It's not created yet, so create it
                    new_genre = Genre(name=genre)
                    db.session.add(new_genre)
                    venue.genres.append(new_genre)  # Create a new Genre item and append it

            # Attempt to save everything
            db.session.commit()
        except Exception as e:
            error_in_update = True
            print(f'Exception "{e}" in edit_venue_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_update:
            # on successful db update, flash success
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('An error occurred. Venue ' + name + ' could not be updated.')
            print("Error in edit_venue_submission()")
            abort(500)


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    # Much of this code is similar to create_venue view
    form = ArtistForm()

    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    # address = form.address.data.strip()
    phone = form.phone.data
    # Normalize DB.  Strip anything from phone that isn't a number
    phone = re.sub(r'\D', '', phone) # e.g. (819) 392-1234 --> 8193921234
    genres = form.genres.data                   # ['Alternative', 'Classical', 'Country']
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website.data.strip()
    facebook_link = form.facebook_link.data.strip()
    
    # Redirect back to form if errors in form validation
    if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_artist_form'))

    else:
        error_in_insert = False

        # Insert form data into DB
        try:
            # creates the new artist with all fields but not genre yet
            new_artist = Artist(name=name, city=city, state=state, phone=phone, \
                seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link, \
                website=website, facebook_link=facebook_link)
            # genres can't take a list of strings, it needs to be assigned to db objects
            # genres from the form is like: ['Alternative', 'Classical', 'Country']
            for genre in genres:
                # fetch_genre = session.query(Genre).filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                fetch_genre = Genre.query.filter_by(name=genre).one_or_none()  # Throws an exception if more than one returned, returns None if none
                if fetch_genre:
                    # if found a genre, append it to the list
                    new_artist.genres.append(fetch_genre)

                else:
                    # fetch_genre was None. It's not created yet, so create it
                    new_genre = Genre(name=genre)
                    db.session.add(new_genre)
                    new_artist.genres.append(new_genre)  # Create a new Genre item and append it

            db.session.add(new_artist)
            db.session.commit()
        except Exception as e:
            error_in_insert = True
            print(f'Exception "{e}" in create_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_insert:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return redirect(url_for('index'))
        else:
            flash('An error occurred. Artist ' + name + ' could not be listed.')
            print("Error in create_artist_submission()")
            abort(500)


@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
    # Deletes a artist based on AJAX call from the artist page
    artist = Artist.query.get(artist_id)
    if not artist:
        # User somehow faked this call, redirect home
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        # Need to hang on to artist name since will be lost after delete
        artist_name = artist.name
        try:
            db.session.delete(artist)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting artist {artist_name}.')
            print("Error in delete_artist()")
            abort(500)
        else:
            # flash(f'Successfully removed artist {artist_name}')
            # return redirect(url_for('artists'))
            return jsonify({
                'deleted': True,
                'url': url_for('artists')
            })


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    
    data = []  # Initialize data list before using it

    for show in shows:
        # Can reference show.artist, show.venue
        data.append({
            "venue_id": show.venue_id,  # Change this line
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    


    return render_template('pages/shows.html', shows=data)



@app.route('/venues/<int:venue_id>/shows', methods=['GET'])
def get_venue_shows(venue_id):
    shows = Show.query.filter_by(venue_id=venue_id).all()
    data = []
    for show in shows:
        data.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.isoformat()
        })
    return jsonify(data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    # renders form. do not touch. (--> nyah nyah!  I touched it!)
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm()

    artist_id = form.artist_id.data.strip()
    venue_id = form.venue_id.data.strip()
    start_time = form.start_time.data

    error_in_insert = False
    
    try:
        new_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
        db.session.add(new_show)
        db.session.commit()
    except Exception as e:
        error_in_insert = True
        print(f'Exception "{e}" in create_show_submission()')
        db.session.rollback()
    finally:
        db.session.close()

    if error_in_insert:
        flash(f'An error occurred.  Show could not be listed.')
        print("Error in create_show_submission()")
    else:
        flash('Show was successfully listed!')
    
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''