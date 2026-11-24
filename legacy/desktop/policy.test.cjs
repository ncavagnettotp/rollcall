const {test} = require('node:test');
const assert = require('node:assert/strict');
const {parseOrigin, allowsNavigation, allowsOriginalWindow} = require('./policy.cjs');

test('accepts a machine-configured HTTPS origin and normalizes it', () => {
  assert.equal(parseOrigin('https://ROLLCALL.test:8443/'), 'https://rollcall.test:8443');
});

test('only the original PDF route can open a child window', () => {
  const origin = 'https://rollcall.test:8443';
  const pdf = '/api/documents/570fdacd-08a1-4b83-95fc-2af4cd993ffa/pdf';
  assert.equal(allowsOriginalWindow(origin, origin + pdf), true);
  assert.equal(allowsOriginalWindow(origin, origin + pdf + '?other=1'), false);
  assert.equal(allowsOriginalWindow(origin, 'https://other.test' + pdf), false);
  assert.equal(allowsOriginalWindow(origin, origin + '/'), false);
});

test('rejects insecure and ambiguous configuration', () => {
  for (const value of [
    null, 'http://rollcall.test', 'https://user@rollcall.test', 'https://rollcall.test/path',
    'https://rollcall.test/?', 'https://rollcall.test/#', 'https://rollcall.test/a/..',
    'https:rollcall.test', 'https://rollcall.test\\', ' https://rollcall.test',
  ]) assert.throws(() => parseOrigin(value), TypeError);
});

test('navigation stays on the exact HTTPS origin', () => {
  const origin = 'https://rollcall.test:8443';
  assert.equal(allowsNavigation(origin, origin + '/api/documents/1/pdf'), true);
  for (const value of [
    'http://rollcall.test:8443', 'https://rollcall.test', 'https://rollcall.test.evil:8443',
    'https://user@rollcall.test:8443', 'file:///tmp/page', 'blob:' + origin + '/id',
    'javascript:void(0)', 'malformed',
  ]) assert.equal(allowsNavigation(origin, value), false);
});
