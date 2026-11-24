const {app, BrowserWindow, dialog, session, Menu} = require('electron');
const {readFileSync} = require('node:fs');
const {isAbsolute, join} = require('node:path');
const {parseOrigin, allowsNavigation, allowsOriginalWindow} = require('./policy.cjs');

const securePreferences = {
  sandbox: true,
  contextIsolation: true,
  nodeIntegration: false,
  nodeIntegrationInSubFrames: false,
  webSecurity: true,
  webviewTag: false,
  devTools: false,
  partition: 'persist:rollcall',
};

function readOrigin() {
  // The unpackaged proof can use a temporary config without writing to ProgramData.
  const override = app.isPackaged ? undefined : process.env.ROLLCALL_PROOF_CONFIG;
  const path = override || join(process.env.ProgramData, 'Rollcall', 'server.json');
  if (!isAbsolute(path)) throw new Error('Configuration path must be absolute.');
  return parseOrigin(JSON.parse(readFileSync(path, 'utf8').replace(/^\uFEFF/, '')).origin);
}

function guardNavigation(contents, allowed) {
  const guard = event => {
    if (!allowed(event.url)) event.preventDefault();
  };
  contents.on('will-frame-navigate', guard);
  contents.on('will-redirect', guard);
  contents.on('will-attach-webview', event => event.preventDefault());
}

async function openRollcall() {
  let origin;
  try {
    origin = readOrigin();
  } catch {
    dialog.showErrorBox('Rollcall setup required',
      'Ask your administrator to provide a valid Rollcall server configuration.');
    app.quit();
    return;
  }

  Menu.setApplicationMenu(null);
  const webSession = session.fromPartition(securePreferences.partition);
  webSession.setPermissionRequestHandler((_contents, _permission, reply) => reply(false));
  webSession.setPermissionCheckHandler(() => false);
  webSession.setDevicePermissionHandler(() => false);

  const window = new BrowserWindow({
    width: 1280, height: 850, title: 'Rollcall', show: false,
    webPreferences: securePreferences,
  });
  const contents = window.webContents;
  guardNavigation(contents, url => allowsNavigation(origin, url));
  contents.setWindowOpenHandler(({url}) => {
    if (!allowsOriginalWindow(origin, url)) return {action: 'deny'};
    return {
      action: 'allow',
      overrideBrowserWindowOptions: {
        parent: window, width: 1000, height: 800, webPreferences: securePreferences,
      },
    };
  });
  contents.on('did-create-window', (child, {url}) => {
    guardNavigation(child.webContents, target => target === url);
    child.webContents.setWindowOpenHandler(() => ({action: 'deny'}));
  });

  while (!window.isDestroyed()) {
    const timeout = setTimeout(() => {
      if (!contents.isDestroyed()) contents.stop();
    }, 12000);
    try {
      await window.loadURL(origin);
      window.show();
      return;
    } catch {
      if (window.isDestroyed()) return;
    } finally {
      clearTimeout(timeout);
    }
    const {response} = await dialog.showMessageBox({
      type: 'warning', title: 'Rollcall unavailable',
      message: 'Rollcall couldn’t connect securely.',
      detail: 'Check your network connection and retry. If the problem continues, contact your administrator.',
      buttons: ['Retry', 'Close'], defaultId: 0, cancelId: 1,
    });
    if (response === 1 && !window.isDestroyed()) window.close();
  }
}

app.on('window-all-closed', () => app.quit());
app.whenReady().then(openRollcall).catch(() => {
  dialog.showErrorBox('Rollcall could not start', 'Contact your administrator.');
  app.quit();
});
