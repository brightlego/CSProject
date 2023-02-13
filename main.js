/* This is the file that runs Electron to create a window.

It works by first, deleting all files in the /static/images folder.
Then it spawns a flask server.
Then it creates a browser window
Finally, it tells that browser window to look at the flask server.
 */

// Importing app to run electron and BrowserWindow to create a window
const { app, BrowserWindow } = require('electron')

// Required to spawn the flask server
const { spawn } = require('node:child_process');

// Required for clearing all the files in /static/images
const fs = require("fs");
const path = require("path");

// Get all the files in ./static/images
fs.readdir('./static/images', (err, files) => {
    // Make sure to throw error if received for easier debugging
    if (err) throw err;
    // For each of the files in the directory
    for (const file of files) {
        // Delete that file. If an error is encountered, throw it for easier
        // debugging
        fs.unlink(path.join('./static/images', file), (err) =>
            {if (err) throw err} );
    }
})

// Spawn the flask server using the local interpreter
const flaskServer = spawn("./interpreters/Python-3.11.1/python", ["app.py"])

// If the server outputs to stdout (prints), carry that output on
flaskServer.stdout.on('data', (data) =>
    process.stdout.write(`${data}`))

// If the server output to stderr (throws an error), display that error
flaskServer.stderr.on('data', (data) =>
    process.stderr.write(`${data}`))

// Report when the flask server terminates
flaskServer.on('close', (code) => {
  console.log(`Flask server exited with code ${code}`);
});

// Function to create the window
const createWindow = () => {
    // Create a new window of default height 600px and width 800px
    const win = new BrowserWindow({
        width: 800,
        height: 600})

    // Wait for 1s before loading the flask server to prevent a race condition
    // where the window is created and attempts to connect to a flask server
    // but that flask server is not yet running
    setTimeout(() => win.loadURL('http://127.0.0.1:5000'), 1000)
}

// Create a window when the electron app is ready
app.whenReady().then(() => createWindow())