#!/usr/bin/env python3

from Class import Com, Config, Display, Hardware, Signal
from Class.Scheduler import Scheduler

if __name__ == "__main__":
    config = Config().load()
    theme = Config().getTheme()

    com = Com(config)
    signal = Signal(com)
    signal.makeHandler(signal.sigHandler)
    display = Display(com, com.serial, config)
    hardware = Hardware()
    scheduler = Scheduler(config, theme, display, com)

    display.displayBitmap(theme)
    display.displayBitmap(config.get(
        'assets_dir', 'assets/') + 'imgs/docker.png', 120, 300)
    scheduler.run({
        'static': 'static_text_informations',
        'dynamic': 'dynamic_text_informations'
    })

    #     # for picture in sorted(os.listdir(config.get('assets_dir', 'assets/') + 'imgs/surf')):
    #     #     threads.append(generateThread(
    #     #         display.displayBitmap, {
    #     #             "bitmap_path": config.get('assets_dir', 'assets/') + 'imgs/surf/' + picture,
    #     #             "x": 100,
    #     #             "y": 300,
    #     #         }))
