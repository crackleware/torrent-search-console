#!/usr/bin/python2

import sys
import glob
import imp
import os
import thread
import re
from optparse import OptionParser

import gtk, gobject

import TorrentSearch.Plugin

parser = OptionParser()
parser.add_option("-t", "--timeout", type="float",
                  action="store", dest="timeout", default=0.0,
                  help="timeout in secs")
parser.add_option("-p", "--plugins", type="str",
                  action="store", dest="plugins", default='.*',
                  help="regexp for plugin selection")
parser.add_option("-n", "--no-kilobytes",
                  action="store_false", dest="kilobytes", default=True,
                  help="don't output size in kilobytes")

class Categories:
    def __getitem__(self, item):
        #print 'Categories.__getitem__:', item
        return ''

class App:
    class options:
        share_dir = '/usr/share'
    def __init__(self):
        self.config = {'disabled_plugins': []}
        self.categories = Categories()
        self.cnt = 0
        self.kilobytes = False
    def notify_plugin_icon(self, plugin):
        #print 'notify_plugin_icon', plugin
        pass
    def notify_plugin_login_failed(self, plugin):
        #print 'notify_plugin_login_failed', plugin
        pass
    def notify_search_finished(self, plugin):
        #print 'notify_search_finished', plugin
        with lock:
            self.cnt -= 1
            #print 'cnt:', self.cnt
            if self.cnt == 0:
                gtk.main_quit()
    def add_row(self, cols):
        print '|'.join(['%s']*len(cols)) % tuple(cols)
    def add_result(self, plugin, item):
        #print 'add_result:', plugin, item
        size = item.size
        if self.kilobytes:
            if size.endswith(' GB'):
                size = '%.1f' % (float(size.split()[0])*1024*1024)
            elif size.endswith(' MB'):
                size = '%.1f' % (float(size.split()[0])*1024)
            elif size.endswith(' KB'):
                size = '%.1f' % float(size.split()[0])
        self.add_row(map(lambda x: str(x).replace('|', ' '), [
                    'result:',
                    plugin.TITLE,
                    size,
                    item.label,
                    item.date,
                    item.seeders,
                    item.leechers,
                    item.category,
                    item.link,
                    ]))
    def add_header_row(self):
        self.add_row([
                'header:',
                'plugin',
                'size',
                'label',
                'date',
                'seeders',
                'leechers',
                'category',
                'link',
                ])
    def download(self, link):
        #print 'download:', link
        pass

def safe_eval(*args):
    #print 'safe_eval:', args
    try: return int(*args)
    except ValueError, e:
        try: return float(*args)
        except ValueError, e:
            raise e

def run(appClass, options, args):
    app = appClass()
    app.kilobytes = options.kilobytes
    
    query = ' '.join(args)
    
    lock = thread.allocate_lock()

    for path in sorted(glob.glob(os.path.join(
                os.environ['HOME'], '.torrent-search', 'search-plugins', '*'))):
        if re.search(options.plugins, os.path.split(path)[-1].lower()):
            app.add_row(['plugin:', path])
            plugin = TorrentSearch.Plugin.load_plugin(app, path)
            mod = sys.modules[plugin.__class__.__module__]
            mod.eval = safe_eval
            with lock: app.cnt += 1
            plugin.search(query)

    with lock:
        if app.cnt == 0:
            return

    app.add_header_row()

    def timeout(*args):
        app.add_row(['timeout!'])
        gtk.main_quit()

    if options.timeout:
        gobject.timeout_add(int(options.timeout*1000), timeout) # ! ret

    gobject.threads_init()
    gtk.main()

    return app

class SilentApp(App):
    def __init__(self):
        App.__init__(self)
        self.rows = []
    def add_row(self, row):
        self.rows.append(row)
    
def run_silently(options, args):
    return run(SilentApp, options, args).rows

if __name__ == '__main__':
    (options, args) = parser.parse_args()
    if not args:
        parser.print_help()
    else:
        run(App, options, args)
