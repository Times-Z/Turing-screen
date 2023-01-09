#!/usr/bin/env python3

from Class import Com, Config, Display, Scheduler, Signal

if __name__ == "__main__":
    configuration: Config = Config()
    config: dict = configuration.load()
    theme = configuration.getTheme()

    com: Com = Com(config)
    signal: Signal = Signal(com)
    signal.makeHandler(signal.sigHandler)
    display: Display = Display(com, com.serial, config)
    scheduler: Scheduler = Scheduler(configuration, theme, display, com)

    scheduler.run({
        'txt_static': 'static_text_informations',
        'txt_dynamic': 'dynamic_text_informations',
        'img_static': 'static_image'
    })

    # for picture in sorted(os.listdir(config.get('assets_dir', 'assets/') + 'imgs/surf')):
    #     threads.append(generateThread(
    #         display.displayBitmap, {
    #             "bitmap_path": config.get('assets_dir', 'assets/') + 'imgs/surf/' + picture,
    #             "x": 100,
    #             "y": 300,
    #         }))
