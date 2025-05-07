   #!/usr/bin/env bash
   # exit on error
   set -o errexit

   pip install -r requirements.txt

   python myapp/manage.py collectstatic --no-input
   python myapp/manage.py migrate