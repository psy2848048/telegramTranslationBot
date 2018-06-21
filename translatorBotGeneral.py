from translatorBot import TranslatorBot
import time, traceback

if __name__ == "__main__":
    translator = TranslatorBot()
    while True:
        try:
            translator.generalTranslation()
        except:
            traceback.print_exc()

        time.sleep(0.5)

