from screeninfo import get_monitors


def size_monitor():
    monitor = get_monitors()[0]
    width = monitor.width
    height = monitor.height

    return width, height
