<img src="assets/logo.png" alt="taskee logo" style="width:140px;"/>
<hr>

`taskee` is a command-line tool for monitoring [Google Earth Engine](https://developers.google.com/earth-engine) tasks that can send notifications to your phone or computer to let you know when your tasks finish. Or fail. No judgement.

![](assets/dashboard.gif)

# Features

- 🔍 Monitor [Google Earth Engine](https://developers.google.com/earth-engine) tasks created with the Python API and/or the Javascript Code Editor
- 💻 Native notifications for Linux, Mac, and Windows
- :speech_balloon: Mobile push notifications for Android
- :tv: Built-in CLI dashboard

# Setup

```bash
pip install taskee
```

Run the setup steps below as needed.  
</br>

<details>
  <summary><b>Earth Engine</b> (required)</summary>
  Set up a <a href="https://developers.google.com/earth-engine">Google Earth Engine</a> account. If you haven't authenticated Earth Engine before, you'll be asked to do so the first time you run <code>taskee</code>.
  
</details></br>

<details>
  <summary><b>Pushbullet</b> (optional)</summary>
  If you want to receive mobile notifications (Android only), you'll need to create or connect an account with <a href="https://pushbullet.com">Pushbullet</a>, download the app on your device(s), and install the <a href="https://github.com/rbrcsk/pushbullet.py">Pushbullet Python API</a> using <code>pip install pushbullet.py</code>.
  Once Pushbullet is installed and you're logged in, go to your <a href="https://www.pushbullet.com/#settings">Account Settings</a>, create an Access Token, and copy the API key. The first time you run <code>taskee</code> with a <code>pushbullet</code> notifier, you'll need to enter your API key. That key will be stored locally so you don't have to enter it again.
</details></br>

<details>
  <summary><b>notify-send</b> (Linux only)</summary>
  Linux users may need to install <code>notify-send</code> to enable <code>native</code> notifications. If <code>taskee</code> is not working with the <code>native</code> notifier, run <code>sudo apt install libnotify-bin</code>.
</details>
</br>


# Usage

`taskee` offers a few different commands which you can see by running `taskee --help`.

```bash
Usage: python -m taskee.cli.cli [OPTIONS] COMMAND [ARGS]...

  Monitor Earth Engine tasks and send notifications.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  start  Start running the notification system.
  tasks  Display a table of current Earth Engine tasks.
  test   Send a test notification.

```

## Starting taskee

The `taskee start` command initializes and runs the notification system. It will continue running until you cancel it, periodically checking your Earth Engine tasks and sending you notifications.

`taskee start` requires one argument: `mode`.

### Choosing a Mode

There are two modes that `taskee start` can run in: `dashboard` and `log`.

`dashboard` shows a live-updating dashboard that makes it easy to visually keep track of your tasks and events.

```bash
taskee start dashboard
```

![A dashboard showing live-updating tasks and events](assets/dashboard.gif)

`log` is designed to be run in the background and prints minimal logs as events occur.

```bash
taskee start log
```

![A terminal showing logs of new events.](assets/log.gif)

### Filtering Events

There are a lot of possible events that can happen to Earth Engine tasks. The list below describes the events recognized by `taskee`.

| Event | Description |
| ----: | :----- |
| *created* | :seedling: A new task is submitted. |
| *started* | :herb: A task starts processing. |
| *attempted* | :fallen_leaf: An attempt fails and the task is restarted. |
| *completed* | :evergreen_tree: A task finished successfully. |
| *failed* | :fire: A task fails to complete. |
| *cancelled* | :axe: The user cancels the task. |
| *error* | :exclamation: `taskee` crashes. |

By default, `taskee` will notify you of `errors` and `completed` or `failed` tasks, but you can specify which events to watch for by listing them when you launch `taskee`. For example:

```bash
taskee start dashboard failed attempted cancelled error
```

You can also use `all` as a shortcut and `taskee` will notify you of all events.

```bash
taskee start dashboard all
```

### Selecting Notifiers

By default, `taskee` will use the `native` notification system built into your computer's operating system. 

![](assets/notification_native_windows.gif)


If you want notifications on other devices, set up Pushbullet and then select it with the `-n --notifier` option.

```bash
taskee start dashboard --notifier pushbullet
```

![](assets/notification_pushbullet.gif)

Like with events, you can use `all` as a shortcut and `taskee` will send both `native` and `pushbullet` notifications.

```bash
taskee start dashboard -n all
```

### Other Options

You can set how often tasks are re-checked (in minutes) using the `-i --interval_mins` option. 

```bash
taskee start dashboard -i 10
```

Note: `taskee` doesn't set a minimum interval, but if updates occur too frequently you may run into rate limits for Earth Engine or Pushbullet.

### Example

Using what we learned above, let's set up `taskee` to start running in `log` mode, check for `cancelled` or `completed` task events, send us notifications using `pushbullet`, and update every `30` minutes.

```bash
taskee start log cancelled completed -n pushbullet -i 30
```

## Other Commands

Aside from running the notification system, `taskee` has a few more commands that may be helpful.


### Task Summaries

The `tasks` command checks your Earth Engine tasks once, giving you a snapshot of your current tasks in a nice, readable table.

```bash
taskee tasks
```

![A table showing details for a list of tasks.](assets/tasks.png)

### Test Notifications

The `test` command sends a mock notification to any notifiers selected with the `-n --notifier` option. You can use this to make sure notifications are set up and working.

```bash
taskee test -n native
```

![](assets/test.gif)
