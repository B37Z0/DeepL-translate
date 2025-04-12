from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from langdetect import detect
from langdetect import DetectorFactory
DetectorFactory.seed = 0 # To ensure consistency in language detection

# Objective: Create a program using only Selenium to communicate with DeepL Translate and translate a piece of text to English
# langdetect is used for purely aesthetic purposes

# ISO 639-1 Language Codes
languages = {
    "af": "Afrikaans", "ar": "Arabic", "bg": "Bulgarian", "bn": "Bengali", "ca": "Catalan",
    "cs": "Czech", "cy": "Welsh", "da": "Danish", "de": "German", "el": "Greek",
    "en": "English", "es": "Spanish", "et": "Estonian", "fa": "Persian", "fi": "Finnish",
    "fr": "French", "gu": "Gujarati", "he": "Hebrew", "hi": "Hindi", "hr": "Croatian",
    "hu": "Hungarian", "id": "Indonesian", "it": "Italian", "ja": "Japanese", "kn": "Kannada",
    "ko": "Korean", "lt": "Lithuanian", "lv": "Latvian", "mk": "Macedonian", "ml": "Malayalam",
    "mr": "Marathi", "ne": "Nepali", "nl": "Dutch", "no": "Norwegian", "pa": "Punjabi",
    "pl": "Polish", "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sk": "Slovak",
    "sl": "Slovenian", "so": "Somali", "sq": "Albanian", "sv": "Swedish", "sw": "Swahili",
    "ta": "Tamil", "te": "Telugu", "th": "Thai", "tl": "Tagalog", "tr": "Turkish",
    "uk": "Ukrainian", "ur": "Urdu", "vi": "Vietnamese", "zh-cn": "Chinese", "zh-tw": "Chinese"}
# Note zh-cn is Simplified Chinese while zh-tw is Traditional Chinese, but DeepL does not make a distinction

def show(step):
    "To print colored text in the terminal to show the program working."
    return '\033[92m' + step + '\033[0m'

def find_element_if_present(id):
    try:
        return driver.find_element(By.ID, id)
    except NoSuchElementException:
        return None

translator = "https://www.deepl.com/en/translator/"
ai = "https://chatgpt.com"
demo = False # True for short text / False for long text

# THIS PROGRAM TRANSLATES USER INPUT INTO (AMERICAN) ENGLISH
# prompt = input(show("Enter a prompt: "))

# Test prompts (short / long)
# prompt = '''Hola, amigo mío. Espero que estés teniendo un buen día.'''
prompt = '''私の名前は吉良良景です。 私は33歳です。 私の家はすべての別荘がある森王の北東部にあり、私は結婚していません。 私は亀湯百貨店の従業員として働いており、遅くとも午後8時までに毎日家に帰ります。 私は喫煙しませんが、時々飲みます。 私は午後11時までにベッドに横たわり、どのような場合でも8時間の睡眠を確保します。 コップ1杯の温かい牛乳を飲んで寝る前に約20分間ストレッチをした後、私は通常、朝まで眠ることに問題はありません。 赤ちゃんのように、朝は疲れもストレスもなく目が覚めます。 前回の検査で問題はなかったと言われました。 私は非常に静かな生活をしたい人だと説明しようとしています。 私は、勝ち負けのような敵に悩まされないように気をつけています。 それが私が社会に対処する方法であり、それが私に幸福をもたらすことを知っています。 しかし、もし私が戦うなら、誰にも負けないでしょう。'''

# Convert prompt to a single line PARAGRAPH* for easier processing later
prompt = prompt.replace('\n', ' ').replace('\r', '')

# Non-English languages using the English alphabet must have accents for accuracy (ex. DeepL has trouble recognizing non-accented French)
language_code = detect(prompt)
language = languages[language_code]
print(show(f"Detected language: {language}."))

if language != "English":
    print(show("Opening translator..."))
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, timeout=20)
    driver.get(translator)
    # driver.fullscreen_window() # for fullscreen

    # Execute Javascript script to remove "Get Extension" pop-up (the pop-up blocks a button that needs to be clicked later)
    driver.execute_script("sessionStorage.setItem(\"LMT_browserExtensionPromo.displayed\", true)")

    # Input prompt into DeepL
    driver.find_element(By.XPATH, "//*[@id=\"textareasContainer\"]/div[1]/section/div/div[1]/d-textarea/div[1]").send_keys(prompt)

    # Wait for initial translation & page to fully load (longer prompts may need a longer wait time)
    driver.implicitly_wait(15)

    driver.execute_script("window.scrollTo(0, 0)") # scroll to top of page
    driver.find_element(By.XPATH, "//*[@id=\"cookieBanner\"]/div/span/button").click() # click on Close Cookie Banner 

    lang_target = find_element_if_present(id="headlessui-popover-button-:rk:") # find Select Target Language element
    if lang_target != None:
        lang_target.click() # click if found
    else:
        driver.find_element(By.ID, "headlessui-popover-button-:rj:").click() # DeepL sometimes uses a different name, not sure why

    driver.find_element(By.XPATH, "//button[8]/div/div/span").click() # click on English (American)

    if demo == True:
        # DeepL splits long text into separate sentence <span> elements so for a demo only the first sentence is used.
        prompt = driver.find_element(By.XPATH, "//*[@id=\"textareasContainer\"]/div[3]/section/div[1]/d-textarea/div/p[1]/span[1]").text

    elif demo == False:
        
        prompt_tl = ""
        i = 1
        element_exists = True

        while element_exists:
            try:
                # Iterate through each <span> element in the first <p> paragraph and retrieve inner text (only for 1st PARAGRAPH*)
                sentence = driver.find_element(By.XPATH, f"//*[@id=\"textareasContainer\"]/div[3]/section/div[1]/d-textarea/div/p/span[{i}]").text
                prompt_tl += f"{sentence} " # add a space after every period
                i += 1
            except NoSuchElementException:
                element_exists = False

        prompt = prompt_tl

'''
NOTE FOR LONG TEXT TRANSLATION:
- In DeepL, the output text box is a <div> with a <p> for every paragraph / empty line (\n). 
- Each <p> is broken into <span> elements, each with a sentence as inner text
- For a single <p> paragraph (single line / no line breaks), the xpath is:
    - "//*[@id="textareasContainer"]/div[3]/section/div[1]/d-textarea/div/p"
'''

print(show(f"The translated prompt is: \n{prompt}"))



'''
Had a huge headache trying to navigate and interact with DeepL using Selenium.
Ended up removing several instructions because elements weren't being located.

For future reference:
- https://stackoverflow.com/questions/46669850/using-aria-label-to-locate-and-click-an-element-with-python3-and-selenium
- for javascript > top tab >> Application > check Local/Session Storage dropdowns for keys and values
    - ex. for the popup, the popup is stored in local storage, but once the popup expires the key/value is updated in session storage
        - Use a sessionStorage.setItem() script to get rid of the popup
'''

# Attempted Solutions for Popup without Javascript (that didn't work):

    # obstruction = driver.find_element(By.CLASS_NAME, "flex size-full items-center justify-end gap-4") # class name from error message
    # ActionChains(driver) \
    #     .move_to_element(obstruction) \
    #     .double_click(obstruction) \
    #     .perform()

    # driver.find_element(By.XPATH, "/div/div/div[2]/button/svg/path ").click()

    # driver.find_element(By.XPATH< "//*[@id="gatsby-focus-wrapper"]/div[2]/div[2]/div[1]/div[2]/div[1]/main/div[3]")