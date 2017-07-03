# import os, sys
# import django
# # from django.conf import settings
#
# SECRET_KEY = 'testtest'
# DEBUG = True
#
#
# def runtests(*test_args):
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gnosisdb.settings')
#     django.setup()
#
#     DIRNAME = os.path.dirname(__file__)
#
#     parent = os.path.dirname(os.path.abspath(__file__))
#     sys.path.insert(0, parent)
#
#     if django.VERSION < (1, 8):
#         from django.test.simple import DjangoTestSuiteRunner
#         failures = DjangoTestSuiteRunner(
#             top_level=os.getcwd(),
#             verbosity=1,
#             interactive=True,
#             failfast=False,
#             keepdb=True
#         ).run_tests(['tests'])
#
#         if failures:
#             sys.exit(failures)
#
#     else:
#         from django.test.runner import DiscoverRunner
#         failures = DiscoverRunner(
#             top_level=os.getcwd(),
#             verbosity=1,
#             interactive=True,
#             failfast=False,
#             keepdb=True
#         ).run_tests(test_args)
#
#         if failures:
#             sys.exit(failures)
#
#
# runtests()