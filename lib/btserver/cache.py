# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of streamondemand 5.
#
# streamondemand 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# streamondemand 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with streamondemand 5.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# Gestiona el cache del servidor torrent:
# Guarda los .torrent generado
# Guarda los .resume de cada torrent
# ------------------------------------------------------------
import os.path
import re
import base64

try:
    from python_libtorrent import get_libtorrent
    lt = get_libtorrent()
except Exception, e:
    import libtorrent as lt

class Cache(object):
    CACHE_DIR='.cache'
    def __init__(self, path):

        if not os.path.isdir(path):
            os.makedirs(path)
        self.path=os.path.join(path, Cache.CACHE_DIR)
        if not os.path.isdir(self.path):
            os.makedirs(self.path)


    def _tname(self, info_hash):
        return os.path.join(self.path, info_hash.upper()+'.torrent')

    def _rname(self, info_hash):
        return os.path.join(self.path, info_hash.upper()+'.resume')

    def save_resume(self,info_hash,data):
        f = open(self._rname(info_hash),'wb')
        f.write(data)
        f.close()

    def get_resume(self, url=None, info_hash=None):
        if url:
            info_hash=self._index.get(url)
        if not info_hash:
            return
        rname=self._rname(info_hash)
        if os.access(rname,os.R_OK):
            f = open(rname, 'rb')
            v = f.read()
            f.close()
            return v

    def file_complete(self, torrent):
        info_hash=str(torrent.info_hash())
        nt=lt.create_torrent(torrent)
        tname=self._tname(info_hash)
        f = open(tname, 'wb')
        f.write(lt.bencode(nt.generate()))
        f.close()



    def get_torrent(self, url=None, info_hash=None):
        if url:
            info_hash=self._index.get(url)
        if not info_hash:
            return
        tname=self._tname(info_hash)
        if os.access(tname,os.R_OK):
            return tname

    magnet_re=re.compile('xt=urn:btih:([0-9A-Za-z]+)')
    hexa_chars=re.compile('^[0-9A-F]+$')
    @staticmethod
    def hash_from_magnet(m):
        res=Cache.magnet_re.search(m)
        if res:
            ih=res.group(1).upper()
            if len(ih)==40 and Cache.hexa_chars.match(ih):
                return res.group(1).upper()
            elif len(ih)==32:
                s=base64.b32decode(ih)
                return "".join("{:02X}".format(ord(c)) for c in s)
            else:
                raise ValueError('Not BT magnet link')

        else:
            raise ValueError('Not BT magnet link')

