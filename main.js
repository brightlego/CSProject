const { app, BrowserWindow } = require('electron')
const { spawn } = require('node:child_process');

const flaskServer = spawn("./interpreters/Python-3.11.1/python", ["app.py"])

flaskServer.stdout.on('data', (data) => process.stdout.write(`${data}`))
flaskServer.stderr.on('data', (data) => process.stderr.write(`${data}`))
flaskServer.on('close', (code) => {
  console.log(`child process exited with code ${code}`);
});

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600})
    setTimeout(() => win.loadURL('http://127.0.0.1:5000'), 500)
}

app.whenReady().then(() => {createWindow()})