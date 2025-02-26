from app import create_app, db
from flask_migrate import Migrate

from app.routes import start_checking_thread

app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)
    with app.app_context():
        start_checking_thread() 
