#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import arrow
import sys
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'show'

    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)
    artist = db.relationship('Artist', back_populates='venues')
    venue = db.relationship('Venue', back_populates='artists')

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500), nullable=False)
    artists = db.relationship('Show', back_populates='venue')


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    venues = db.relationship('Show', back_populates='artist')


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # List for storing venues data
    data = list()

    # Go through each distinct city,state location
    city_state = db.session.query(Venue.city, Venue.state).distinct()
    for cs in city_state:
        
        # List for storing venues associated to a specific city,state location
        venues = list()
        
        # Go through all venues associated to a specific city,state location
        venue_list = db.session.query(Venue.id, Venue.name).filter(Venue.city == cs.city, Venue.state == cs.state).all()
        for vl in venue_list:
            venue_data = {
                'id': vl.id,
                'name': vl.name,
                'num_upcoming_shows': Show.query.filter(Show.venue_id == vl.id, Show.start_time > str(arrow.utcnow())).count()
            }
            venues.append(venue_data)

        city_data = {
            'city': cs.city,
            'state': cs.state,
            'venues': venues,
        }
        data.append(city_data)

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search on venues with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    
    data = [{'id': venue.id, 'name': venue.name, 'num_upcoming_shows': Show.query.filter(Show.venue_id == venue.id, Show.start_time > str(arrow.utcnow())).count()} for venue in venues]

    response={
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)

    # Get past and upcoming shows
    shows = Show.query.join(Artist).filter(Show.venue_id == venue_id)
    past_shows = shows.filter(Show.start_time < str(arrow.utcnow())).all()
    upcoming_shows = shows.filter(Show.start_time > str(arrow.utcnow())).all()

    # Lists for past and upcoming shows data
    past_shows_list = list()
    upcoming_shows_list = list()

    for show in past_shows:
        sd = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': f'{str(show.start_time)}Z',
        }
        past_shows_list.append(sd)
    
    for show in upcoming_shows:
        sd = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': f'{str(show.start_time)}Z',
        }
        upcoming_shows_list.append(sd)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False

    try:
        """
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        genres = request.form.getlist('genres')
        seeking_description = request.form.get('seeking_description')
        seeking_talent = request.form.get('seeking_talent', False)
        website = request.form.get('website')
        """
        venue = Venue(**request.form)
        
        
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = db.session.query(Artist.id, Artist.name).all()
    data = [{'id': artist[0], 'name': artist[1]} for artist in artists]
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    
    data = [{'id': artist.id, 'name': artist.name, 'num_upcoming_shows': Show.query.filter(Show.artist_id == artist.id, Show.start_time > str(arrow.utcnow())).count()} for artist in artists]

    response={
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)

    # Get past and upcoming shows
    shows = Show.query.join(Venue).filter(Show.artist_id == artist.id)
    past_shows = shows.filter(Show.start_time < str(arrow.utcnow())).all()
    upcoming_shows = shows.filter(Show.start_time > str(arrow.utcnow())).all()

    # Lists for past and upcoming shows data
    past_shows_list = list()
    upcoming_shows_list = list()

    for show in past_shows:
        sd = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': f'{str(show.start_time)}Z',
        }
        past_shows_list.append(sd)
    
    for show in upcoming_shows:
        sd = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': f'{str(show.start_time)}Z',
        }
        upcoming_shows_list.append(sd)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue={
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = list()
    shows = Show.query.all()
    
    for show in shows:
        venue_data = db.session.query(Venue.name).filter(Venue.id == show.venue_id).first()
        artist_data = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).first()

        sd = {
            'venue_id': show.venue_id,
            'venue_name': venue_data.name,
            'artist_id': show.artist_id,
            'artist_name': artist_data.name,
            'artist_image_link': artist_data.image_link,
            'start_time': f'{str(show.start_time)}Z',
        }
        data.append(sd)

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(host='0.0.0.0', port=port)
'''
