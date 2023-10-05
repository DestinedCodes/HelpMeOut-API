from helpmeout import app, db

# Create all database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Run the Flask app
    app.run()

