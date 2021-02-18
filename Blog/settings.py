"""
Django settings for Blog project.

Generated by 'django-admin startproject' using Django 2.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys


def env_to_bool(env, default):
    str_val = os.environ.get(env)
    return default if str_val is None else str_val == 'True'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wj_k3+5azjx!@e*y5zdi6vfk(9477m9g8(&njp@bq1++x#pn^^'

# SECURITY WARNING: don't run with debug turned on in production!

# DEBUG = env_to_bool('DJANGO_DEBUG', True)
# 开发环境，调试模式
DEBUG = True
# 生产环境
# DEBUG = False
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# 为空只有本机能够访问
ALLOWED_HOSTS = []

# 局域网内的机器都能访问
# ALLOWED_HOSTS = ["*"]

# 允许被所有的机器访问
# ALLOWED_HOSTS = ["0.0.0.0"]


# Application definition
# 注册APP
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'blog',
    'django_summernote', #后台富文本
    # 'tinymce', #tinymce富文本
    'haystack',
    'comment',

]

# summernote富文本配置
# SUMMERNOTE_CONFIG = {
#     'iframe': True,
#     'airMode': False,
#     'styleWithSpan': False,
#     'width': '80%',
#     'height': '480',
#     'lang': 'zh-CN'
# }


# tinymce富文本配置
# TINYMCE_DEFAULT_CONFIG = {
#     'theme': 'advanced',
#     'width': 800,
#     'height': 600,
# }


# 中间件,注意中间件的顺序
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Blog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 模板的存放目录,如果未设置,django会自动将每个应用中的templates目录作为模板的存放目录
        # 'DIRS': [],
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
        ],
        # 是否自动搜索应用中的templates目录
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Blog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': "Blog",
#         'USER': 'root',
#         'PASSWORD': '123456',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DJANGO_MYSQL_DATABASE') or 'Blog',
        'USER': os.environ.get('DJANGO_MYSQL_USER') or 'root',
        'PASSWORD': os.environ.get('DJANGO_MYSQL_PASSWORD') or '123456',
        'HOST': os.environ.get('DJANGO_MYSQL_HOST') or 'LOCALHOST',
        'PORT': int(os.environ.get('DJANGO_MYSQL_PORT') or 3306),
        'OPTIONS': {
            'charset': 'utf8',
        },
    },
    # 从
    'slaver': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DJANGO_MYSQL_DATABASE') or 'db_blog',
        'USER': os.environ.get('DJANGO_MYSQL_USER') or 'root',
        'PASSWORD': os.environ.get('DJANGO_MYSQL_PASSWORD') or '123456',
        'HOST': os.environ.get('DJANGO_MYSQL_HOST') or '127.0.0.1',
        'PORT': int(os.environ.get('DJANGO_MYSQL_PORT') or 3306),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# 数据库主从结构,实现读写分离
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'master_blog_db',
#         'USER': 'root',
#         'PASSWORD': '123456',
#         'HOST': '127.0.0.1',
#         'PORT': '3306'
#     },
#     'slaver': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'slaver_blog_db',
#         'USER': 'root',
#         'PASSWORD': '123456',
#         'HOST': '127.0.0.1',
#         'PORT': '3306'
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-Hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True
# 在数据库中存储的时间仍然是UTC时间,但是显示的时候会按照实际的配置文件进行显示
# USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 关闭自动补全链接斜杠
# APPEND_SLASH = False


# 缓存配置
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'my_cache_table',
#         'TIMEOUT': 60,
#         'OPTIONS': {
#             'MAX_ENTRIES': 300,
#         },
#         'KEY_PREFIX': 'TYCARRY',
#         'VERSION': '1',
#     }
# }

# 基于redis的缓存实现
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         },
#         'TIMEOUT': 60 * 60 * 24
#     }
# }

# 多缓存
CACHES = {
    # 数据库缓存
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
        'TIMEOUT': 60,
    },
    # redis缓存
    'redis_backend': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 60
    }
}


# logging settings
# 配置日志输出到本地文件
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logging.log'),
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

# 日志信息输出到终端显示
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
#         }
#     }
# }


# LOGGING_CONFIG = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     # 格式化器
#     'formatters': {
#         'verbose': {
#             'format': '{leavename} {asctime} {module} {process: d} {thread: d} {message}',
#             # 'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d %(module)s] %(message)s',
#             'style': {},
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': {},
#         }
#     },
#     # 过滤器
#     'filters':{
#         'special': {
#             '()': 'project.logging.SpecialFilter',
#             'foo': 'bar',
#         },
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#     },
#     # 处理器
#     'handlers': {
#         'log_file': {
#             'level': 'INFO',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': 'logging.log',
#             'maxBytes': 16777216, #16M
#             'formatter': 'verbose',
#         },
#         'console': {
#             'level': 'INFO',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'filters': ['special'],
#         },
#     },
#     # 日志
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'propagate': True,
#         },
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'myproject.custom': {
#             'handlers': ['console', 'mail_admins'],
#             'level': 'INFO',
#             'filters': ['special'],
#         }
#     }
# }

# whoosh search settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'Blog.whoosh_cn_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

# 自动更新索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# setting Elasticsearch as search engine
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9000/',
#         'INDEX_NAME': 'haystack',
#     },
# }

# Xapian
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'xapian_backend.XapianEngine',
#         'PATH': os.path.join(os.path.dirname(__file__), 'xapian_index'),
#     },
# }

TIME_FORMAT = '%Y-%n-%d %H-%M-%S'
DATE_TIME_FORMAT = '%Y-%m-%d'

# bootstrap color styles
BOOTSTRAP_COLOR_TYPES = [
    'default', 'primary', 'success', 'info', 'warning', 'danger'
]

# paginate
PAGINATE_BY = 10
# http cache timeout
CACHE_CONTROL_MAX_AGE = 2592000

# STATICFILES_FINDERS = (
#     'django.contrib.staticfiles.finder.FileSystemFinder',
#     'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#     'compressor.finders.CompressorFinder',
# )
# 压缩
COMPRESS_ENABLED = True

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluterFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter'
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/media/'
