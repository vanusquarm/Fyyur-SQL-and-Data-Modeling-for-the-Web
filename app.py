#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from tokenize import String
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler, raiseExceptions
from flask_wtf import Form
from sqlalchemy import false, true, ARRAY, func
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
#database connection url is specified in config.py file 
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id  = db.Column(db.Integer, primary_key=True) 
    name  = db.Column(db.String, nullable=False)
    genres  = db.Column(db.ARRAY(db.String))
    address  = db.Column(db.String, nullable=False )
    city  = db.Column(db.String, nullable=False ) 
    state  = db.Column(db.String, nullable=False)
    phone  = db.Column(db.String )
    website_link  = db.Column(db.String )
    facebook_link  = db.Column(db.String )
    seeking_talent  = db.Column(db.Boolean, default = False)
    seeking_description  = db.Column(db.Text)  
    image_link  = db.Column(db.String )
    show_id = db.relationship('Show', backref='venue', lazy=True)

    # def __repr__(self):
    #   return f'<Venue {self.id}: "{self.name}", "{self.city}", "{self.state}" ... >'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    #DONE

class Artist(db.Model):
    __tablename__ = 'Artist'

    id  = db.Column(db.Integer, primary_key=True) 
    name  = db.Column(db.String, nullable=False) 
    genres  = db.Column(db.ARRAY(db.String))
    city  = db.Column(db.String )
    state  = db.Column(db.String )
    phone  = db.Column(db.String )   
    website_link  = db.Column(db.String )  
    facebook_link  = db.Column(db.String )
    seeking_venue  = db.Column(db.Boolean) 
    seeking_description  = db.Column(db.String )
    image_link  = db.Column(db.String )
    show_id = db.relationship('Show', backref='artist', lazy=True)

    # def __repr__(self):
    #   return f'<Artist {self.id}: "{self.name}", "{self.city}", "{self.state}" ... >'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)

    # def __repr__(self):
    #   return f'<Show {self.id}: "{self.start_time}", "{self.venue_id}", "{self.artist_id}" ... >'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    #DONE

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# User Functions.
#----------------------------------------------------------------------------#

def createDictFromList(keylist,vallist):
  '''
    create dictionary with key and value lists
    eg. createDictFromList({'a','b','c'},[4,2,5]) returns {'a':4,'b':2,'c':5}
        createDictFromList(['a','b','c'],[4,9]) returns {'a':4,'b':9,'c':0}
  '''
  if (isinstance(vallist,str)):
    vallist = vallist.split(',') #convert to list if a comma-separated string
  if (isinstance(keylist,str)):
    keylist = keylist.split(',') #convert to list if a comma-separated string  
    
  thisdict = dict.fromkeys(keylist)
  #print(thisdict)
  
  for i,k in enumerate(thisdict.keys(),0):
    try:
      thisdict[k] = vallist[i]
    except:
      return thisdict
  return thisdict
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  subquery = db.session.query(Venue.city, Venue.state, func.concat_ws(',',Venue.id, Venue.name).label('venues'))\
    .group_by(Venue.name, Venue.id).subquery()
  result = db.session.query(subquery.c.city, subquery.c.state, func.array_agg(subquery.c.venues).label('venues_agg'))\
    .group_by(subquery.c.city, subquery.c.state).all()
  #>>> [('San Francisco', 'CA', ['3,Park Square Live Music & Coffee', '1,The Musical Hop']), 
  #     ('New York', 'NY', ['2,The Dueling Pianos Bar'])]
  data = []
  for row in result:
    data_item = {
    "city": row.city,
    "state": row.state,
    "venues": [createDictFromList(['id','name'],row_venue) for row_venue in row.venues_agg] 
    }
    data.append(data_item)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  result_venue =  db.session\
    .query(Venue.id, Venue.name)\
      .filter(Venue.name.ilike('%'+search_term+'%'))\
        .all()
  response={
    "count": len(result_venue),
    "data": [createDictFromList(["id","name"], row) for row in result_venue]
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = db.session.query(Artist.id,Artist.name,Artist.image_link,Show.start_time)\
    .join(Show).filter(Show.venue_id == venue_id).all()
  
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  
  for show in shows:
    show_data = {
    'venue_id': show.id,
    'venue_name': show.name,
    'venue_image_link': show.image_link,
    'start_time': show.start_time.isoformat()
    }
    if show.start_time <= datetime.now():
        data['past_shows'].append(show_data)
    else:
      data['upcoming_shows'].append(show_data)        

  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  db.session.close()
  

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
  error = False
  data = {}
  try:
    venue = Venue(**request.form)
    db.session.add(venue)
    db.session.commit()
    # TODO: modify data to be the data object returned from db insertion
    data['name'] = venue.name
    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    abort (400)
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  if error:
      abort(500)
  else:
      return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist.id, Artist.name).all() 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  result_artist =  db.session\
    .query(Artist.id, Artist.name)\
      .filter(Artist.name.ilike('%'+search_term+'%'))\
        .all()

  # Add this filter to filter(Show.start_time > datetime.now())
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  
  response={
    "count": len(result_artist),
    "data": [createDictFromList(["id","name","num_upcoming_shows"], row) for row in result_artist]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = db.session.query(Venue.id,Venue.name,Venue.image_link,Show.start_time)\
    .join(Show).filter(Show.artist_id == artist_id)
  
  data = {
  'id': artist.id,
  'name': artist.name,
  'genres': artist.genres,
  'city': artist.city,
  'state': artist.state,
  'phone': artist.phone,
  'website_link': artist.website_link,
  'facebook_link': artist.facebook_link,
  'seeking_venue': artist.seeking_venue,
  'seeking_description': artist.seeking_description,
  'image_link': artist.image_link,
  'past_shows': [],
  'upcoming_shows': [],
  'past_shows_count': 0,
  'upcoming_shows_count': 0
  }
  for show in shows:
      show_data = {
      'venue_id': show.id,
      'venue_name': show.name,
      'venue_image_link': show.image_link,
      'start_time': show.start_time.isoformat()
      }
      if show.start_time <= datetime.now():
          data['past_shows'].append(show_data)
      else:
        data['upcoming_shows'].append(show_data)        

  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  db.session.close()
  

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    # Updating with non-null value in update_info
    update_info = request.form
    artist = Artist.query.get(artist_id)
    for k,v in update_info.items():
      if v not in [None,""]:
        artist.__dict__[k] = v #update attribute with new values

    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return 1 #redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    # Updating with non-null value in update_info
    update_info = request.form
    venue = Venue.query.get(venue_id)
    for k,v in update_info.items():
      if v not in [None,""]:
        venue.__dict__[k] = v #update attribute with new values

    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
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
  error = False
  data = {}
  try:
    artist = Artist(**request.form)
    db.session.add(artist)
    db.session.commit()
    # TODO: modify data to be the data object returned from db insertion
    data['name'] = artist.name
    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    abort (400)
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
 



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = db.session\
    .query(\
      Show.venue_id, \
        Venue.name.label('venue_name'),\
           Show.artist_id, Artist.name.label('artist_name'),\
              Artist.image_link.label('artist_image_link'), \
                func.to_char(Show.start_time , 'YYYY-MM-DD HH24:MI:SS').label('start_time')\
                  )\
      .join(Venue, Venue.id==Show.venue_id)\
        .join(Artist, Artist.id==Show.artist_id).all()

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
  error = False
  try:
    show = Show(**request.form)
    db.session.add(show)
    db.session.commit()
  except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
  finally:
      db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    abort (400)
  else:
    # on successful db insert, flash success
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
    app.debug = True
    app.run(host='127.0.0.1', port=5000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
