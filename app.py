from datetime import datetime
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = "myapp1234"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = os.getenv('USER')
app.config["MAIL_PASSWORD"] = os.getenv('PASS')
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Model
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    date = db.Column(db.String)
    occupation = db.Column(db.String(80))

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        first_name = request.form["first_name"]
        email = request.form["email"]
        date = request.form["date"]
        time = request.form["time"]
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        occupation = "N/A"


        form = Form(first_name=first_name, email=email, date=date_obj, occupation=occupation)
        db.session.add(form)
        db.session.commit()


        message_body = f"Thank you for your submission, {first_name}. " \
                       f"Here are your details:\n\n" \
                       f"First Name: {first_name}\n" \
                       f"Email: {email}\n" \
                       f"Available day to talk: {date}\n" \
                       f"Available time: {time}\n" \
                       f"\n\nThank you!"

        # Create message for recipient
        message = Message(subject="New form submission",
                          sender=app.config["MAIL_DEFAULT_SENDER"],
                          recipients=[email],
                          body=message_body)

        # Send message to recipient
        try:
            mail.send(message)
            flash(f"Thank you {first_name}, it was sent successfully, I look forward to talking with you.", "success")
        except Exception as e:
            flash("Failed to send email. Please try again later.", "danger")
            app.logger.error(f"Failed to send email: {str(e)}")

        # Send copy of message to default sender (yourself)
        try:
            message_copy = Message(subject="Copy of form submission",
                                   sender=app.config["MAIL_DEFAULT_SENDER"],
                                   recipients=[app.config["MAIL_DEFAULT_SENDER"]],
                                   body=message_body)
            mail.send(message_copy)
        except Exception as e:
            app.logger.error(f"Failed to send copy of email: {str(e)}")

    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
