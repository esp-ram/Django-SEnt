# Django-SEnt

SEnt is a simple system made with Django for students to submit their exams. It delivers a zip with the files submitted (properly named) via email.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to the required libraries.

```bash
pip install -r requirements.txt
```


## Usage
Run these usual Django commands.

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
The project makes use of the environment variables, so you'll need a .env file with the following variables.
```bash
AES_KEY_SIZE # The size in bytes of the AES key.
AES_KEY # The AES key.

DETA_SECRET # The deta secret key.
DETA_DB_NAME # A name for the deta db.
EMAIL_HOST # The email host.
EMAIL_PORT # The email port.
EMAIL_HOST_USER # The email from where the zips are sent.
EMAIL_HOST_PASSWORD # The password for that email.
CC_EMAIL # An email to CC all the email sent (optional).

DJANGO_SECRET_KEY # the django secret key.
```


## Made with
- Django
- [Deta](https://deta.sh)
- [Cryptography](https://pypi.org/project/cryptography/) - The files are encripted (AES with CBC) before uploading them to Deta.


## Scripts
[Here](https://github.com/esp-ram/Scripts-SEnt) you can find a few scripts for this project.


## License
[MIT](https://choosealicense.com/licenses/mit/)
