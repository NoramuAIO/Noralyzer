from app import create_app, db
from app.utils import init_default_data

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        init_default_data()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
