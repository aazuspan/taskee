# taskee

![](assets/preview_windows.jpg)

## Description

`taskee` is a tool for monitoring `Google Earth Engine` tasks. It runs in the background and can send notifications to your phone or computer to let you know when your tasks finish (or fail 🤫).

## Features

- 🔍 Monitor [Google Earth Engine](https://developers.google.com/earth-engine) tasks created with the Python API and/or the Javascript Code Editor
- 💻 Native notifications for Linux, Mac, and Windows
- 📱 Mobile push notifications for Android
- 🐍 Run in an interactive python shell or through a CLI

## Setup

### 1. Install from PyPI
First, install the `taskee` package from PyPI.

```posh
pip install taskee
```

### 2. Set up Earth Engine
Next, set up a [Google Earth Engine](https://developers.google.com/earth-engine) account. If you haven't authenticated Earth Engine before, you'll be asked to do so the first time you run `taskee.initialize()`.

### 3. Set up Pushbullet (Optional)
If you want to receive mobile notifications (Android only), you'll need to create or connect an account with [Pushbullet](https://pushbullet.com), download the app on your device(s), and install the [Pushbullet Python API](https://github.com/rbrcsk/pushbullet.py). 

```posh
pip install pushbullet.py
```

Once you're logged in, go to your [Account Settings](https://www.pushbullet.com/#settings), create an Access Token, and copy the API key. The first time you run `taskee.initialize()` with a `pushbullet` notifier, you'll need to enter your API key. That key will be stored locally so you don't have to enter it again.

### 4. Set up notify-send (Linux only)
Linux users may need to install `notify-send` to enable `native` notifications. Run the following terminal command to check if `notify-send` is working.

```posh
notify-send 'This is a test'
```

If the command above didn't work, run the command below.

```posh
sudo apt install libnotify-bin
```

## Usage

<details>
  <summary><b>Interactive</b></summary></br>

One way to run `taskee` is to set up an interactive Python shell or Jupyter kernel. 

Just import `taskee`, initialize the `Watcher` object, and start watching for tasks.
```python
import taskee

watcher = taskee.initialize()
watcher.watch()
```

### Selecting a Notifier

By default, `taskee` will use the `native` notification system built into your computer's operating system. If you want notifications on other devices, [set up Pushbullet](#3-set-up-pushbullet-optional) and use it by passing `pushbullet` to the `notifiers` argument.

```python
watcher = taskee.initialize(notifiers="pushbullet")
```

You can use both notifiers by passing a list with both notifiers...

```python
watcher = taskee.initialize(notifiers=["native", "pushbullet"])
```

Or use the shorcut keyword `all`.

```python
watcher = taskee.initialize(notifiers="all")
```

### Filtering Events

There are a lot of [possible events](#events) that can happen to Earth Engine tasks. By default, `taskee` will notify you when a task completes or fails, but you can specify which events to watch for using the `watch_for` argument.

```python
watcher.watch(watch_for=["attempted", "failed", "cancelled"])
```

Once again, `all` is a convenient keyword if you want to use all available events.

```python
watcher.watch(watch_for="all")
```

### Other Options

You can set how often tasks are re-checked using the `interval_minutes` keyword...

```python
watcher.watch(interval_minutes=5)
```

And modify how much information is logged to the console using the `logging_level` argument and [this list of levels](https://docs.python.org/3/library/logging.html#levels).

```python
watcher = taskee.initalize(logging_level="DEBUG")
```

</details>
  
  
<details>
  <summary><b>Command Line</b></summary></br>
  
You can also run `taskee` with the command line interface. By default, the command below will watch for `completed` and `failed` events every 15 minutes and notify you with `native` notifications.

```posh
python -m taskee.cli
```

You can watch for additional events by providing a list of events (case-insensitive).

```posh
python -m taskee.cli completed failed attempted
```

Or use `all` to monitor any event type.
```posh
python -m taskee.cli all
```

You add notifiers using the `--notifier` or `-n` option. Like with events, you can use `all` as a shortcut.
```posh
python -m taskee.cli -n native -n pushbullet
```

And you can adjust the update interval using the `--interval_mins` or `-i` option.
```posh
python -m taskee.cli -i 10
```

Putting it all together, the command below will watch for `failed` and `attempted` events using the `pushbullet` notifier every `5` minutes.
```posh
python -m taskee.cli failed attempted -n pushbullet -i 5
```

For help:
```posh
python -m taskee.cli --help
```
</details>

## Events

When an Earth Engine task is updated, it creates an event. You can choose which type of events you're interested from the list below.

| Event | Description |
| ----: | :----- |
| Created | A new task is submitted. |
| Started | A task starts processing. |
| Attempted | An attempt fails and the task is restarted. |
| Completed | A task finished successfully. |
| Failed | A task fails to complete. |
| Cancelled | The user cancels the task. |
