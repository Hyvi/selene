# -*- coding: utf-8 *-*
import logging
import os
import tornado.web
import tornado.gen

from bson import SON
from motor import Op
from selene import smtp
from selene.web import routes, ui_modules
from tornado.options import options as opts


class Selene(tornado.web.Application):

    def __init__(self, db):
        self.db = db
        self.smtp = smtp.SMTP()
        self.theme_path = os.path.join(opts.themes_directory,
                                       opts.selected_theme)
        self.setup_translations()
        self.setup_fts()
        settings = {
            'login_url': '/login',
            'static_path': os.path.join(self.theme_path, 'static'),
            'template_path': os.path.join(self.theme_path, 'templates'),
            'xsrf_cookies': True,
            'cookie_secret': opts.cookie_secret,
            'ui_modules': ui_modules,
            'debug': opts.debug
        }
        if opts.static_url_prefix:
            settings['static_url_prefix'] = opts.static_url_prefix
        if opts.twitter_consumer_key and opts.twitter_consumer_secret:
            settings['twitter_consumer_key'] = opts.twitter_consumer_key
            settings['twitter_consumer_secret'] = opts.twitter_consumer_secret
        tornado.web.Application.__init__(self, routes.urls +
            [(r"/(favicon\.ico)", tornado.web.StaticFileHandler,
            {'path': settings['static_path']})], **settings)

    @tornado.gen.engine
    def setup_fts(self):
        # TODO: Should be used with a sync db connection.
        if opts.db_use_fts:
            try:
                yield Op(self.db.connection.admin.command,
                    SON([('getParameter', 1),
                            ('textSearchEnabled', 1)]))['textSearchEnabled']
                yield Op(self.db.posts.ensure_index,
                    [('plain_content', 'text')])
            except:
                opts.db_use_fts = False
                logging.warning('Full text search is probably not activated '
                    'on MongoDB server, If you want to activated it, use 2.4 '
                    'version and issue the following command on admin '
                    'database:\n db.runCommand({ setParameter: 1, '
                    'textSearchEnabled: true })')

    def setup_translations(self):
        tornado.locale.LOCALE_NAMES['zh_HK'] = {
            'name_en': 'Chinese (Hong Kong)',
            'name': '\u4e2d\u6587(\u7e41\u9ad4)'
        }
        tornado.locale.load_translations("translations")
        tornado.locale.set_default_locale(opts.default_locale)
        logging.info('Loaded translations: {}.'.format(
            ', '.join(sorted([v['name_en'] for k, v in
                list(tornado.locale.LOCALE_NAMES.items()) if k in
                tornado.locale.get_supported_locales()]))))
