from datetime import datetime
from app import app, db, Venue, Artist, Show

def populate_shows():
    reference_shows = [
        {
            "venue_name": "The Musical Hop",
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z"
        },
        {
            "venue_name": "Park Square Live Music & Coffee",
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        },
        {
            "venue_name": "Park Square Live Music & Coffee",
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        },
        {
            "venue_name": "Park Square Live Music & Coffee",
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        },
        {
            "venue_name": "Park Square Live Music & Coffee",
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }
    ]

    with app.app_context():
        try:
            for ref_show in reference_shows:
                # Get or create venue by name
                venue = Venue.query.filter_by(name=ref_show["venue_name"]).first()
                if not venue:
                    venue = Venue(name=ref_show["venue_name"])
                    db.session.add(venue)
                    db.session.commit()

                # Get or create artist by name
                artist = Artist.query.filter_by(name=ref_show["artist_name"]).first()
                if not artist:
                    artist = Artist(name=ref_show["artist_name"], image_link=ref_show["artist_image_link"])
                    db.session.add(artist)
                    db.session.commit()

                # Check if show exists by venue_id, artist_id, and start_time
                start_time_dt = datetime.fromisoformat(ref_show["start_time"].replace("Z", "+00:00"))
                existing_show = Show.query.filter_by(venue_id=venue.id, artist_id=artist.id, start_time=start_time_dt).first()
                if not existing_show:
                    new_show = Show(venue_id=venue.id, artist_id=artist.id, start_time=start_time_dt)
                    db.session.add(new_show)
                    db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    populate_shows()
    print("Shows and related artists/venues have been ensured in the database successfully.")
