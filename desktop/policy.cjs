function parseOrigin(value) {
  if (typeof value !== 'string' || !/^https:\/\/[^/\\?#@\s]+\/?$/i.test(value)) {
    throw new TypeError('Rollcall requires an HTTPS origin.');
  }
  return new URL(value).origin;
}

function allowsNavigation(origin, value) {
  const url = URL.parse(value);
  return !!url && url.protocol === 'https:' && url.origin === origin &&
    !url.username && !url.password;
}

function allowsOriginalWindow(origin, value) {
  if (!allowsNavigation(origin, value)) return false;
  const url = new URL(value);
  return !url.search && !url.hash &&
    /^\/api\/documents\/[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\/pdf$/i.test(url.pathname);
}

module.exports = {parseOrigin, allowsNavigation, allowsOriginalWindow};
