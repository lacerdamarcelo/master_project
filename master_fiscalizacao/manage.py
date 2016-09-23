#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "master_fiscalizacao.settings")
    os.popen('ln -s ' + os.path.dirname(os.path.abspath(__file__)) + '/master_fiscalizacao/site_media/media ' + os.path.dirname(os.path.abspath(__file__)) + '/formulario_vistoria/static/media ')
    os.popen('rm -rf ' + os.path.dirname(os.path.abspath(__file__)) + '/master_fiscalizacao/site_media/media/media')
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
