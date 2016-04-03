location.__defineGetter__('href', ()=>'https://www.foo.com/bar.baz');
importScripts('victim.js');
