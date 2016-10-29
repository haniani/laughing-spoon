# -*- coding: utf-8 -*-

import os 
import fnmatch
import locale

import flask
from flask import render_template
from flask import Flask
from flask import Markup
from flask import abort
from flask import jsonify
from flask import url_for
from flask import redirect 
from flask import request
from flask import json

from datetime import datetime
from markdown import markdown


try:
    from os import getuid

except ImportError:
    def getuid():
        return 4000

app = Flask(__name__)
app.config['ASSETS_DEBUG'] = True
app.debug = True

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')  

def format_post(item):  # Work with markdown
    bits = item.split('_', 1)
    date = datetime.strptime(bits[0], '%Y%m%d')
    title = bits[1].replace('_', ' ').replace('.md', '').title()
    slug = title.lower().replace(' ', '-')
    
    return {'date': date, 'title': title, 'slug': slug}

def get_post_dir():
    return os.path.dirname(os.path.abspath(__file__)) + '/posts'  # Dir with posts

def get_post_items():  # Sort posts 
    items = os.listdir(get_post_dir())
    items.sort(reverse=True)    #сортируем от более новых к старым
    return items

def get_posts():  # Get all posts
    posts = []
    for item in get_post_items():
        if item[0] == '.' or item[0] == '_':
            continue
        post = format_post(item)
        posts.append(post)

    return posts

@app.template_filter('date_format')  # Good date view
def date_format(timestamp):
    return timestamp.strftime('{S} %B, %Y').replace('{S}', str(timestamp.day))

@app.errorhandler(404)  # For errors
def _404(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def _500(e):
    return render_template('errors/500.html'), 500



@app.route('/')
@app.route('/index')  # Main page
def index():

    try:
        template = render_template('index.html', posts=get_posts())
        return template
    except:
        abort(500)

@app.route("/gusinafamily")
def gusinafamily():
    return flask.render_template('gusinafamily.html')

@app.route("/about")
def about():
    return flask.render_template('about.html')

@app.route("/screenshots")
def screenshots():
    return flask.render_template('screenshots.html')


@app.route('/page/<slug>')  # Static
def page(slug):
    try:
        content = app.open_resource('pages/%s.md' % slug.replace('-', '_'), 'r').read()
        content = Markup(markdown(content))

        title = slug.replace('-', ' ').title()
        template = render_template('page.html', content=content, page_title=title)

        return template
    except:
        abort(404)


@app.route('/post/<slug>')  # Posts in blog
def post(slug):
    try:
        post = None
        for item in get_post_items():
            if fnmatch.fnmatch(item, '*_%s.md' % slug.replace('-', '_')):
                post = item
                break

        content = app.open_resource('posts/%s' % post, 'r').read()
        content = Markup(markdown(content))
        title = format_post(post)['title']
        date = format_post(post)['date']
        template = render_template('post.html', content=content, page_title=title, post_date=date)

        return template
    except:
        abort(404)

@app.route('/post_len', methods=['GET', 'POST'])
def post_len():
    count = request.form['counter']
    if len(count) > 140:
        return json.dumps({'len': str(len(count))+ " <font color=\"red\">#not_for_twitter</font>"})
    else:
        return json.dumps({'len': str(len(count))+ " <font color=\"green\">#good_for_twitter</font>"})

if __name__ == '__main__':
    app.run()
