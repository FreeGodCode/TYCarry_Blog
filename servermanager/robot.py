import os

robot = WeRoBot(token=os.environ.get('DJANGO_WEROBOT_TOKEN') or 'lylinux', enable_session=True)

memstorage = MemcacheStorage()