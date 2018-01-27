from captcha.image import ImageCaptcha
import string
import random
import os
import shutil

def reset_dir(out_dir):
    shutil.rmtree(out_dir,ignore_errors=True)
    os.makedirs(out_dir)

if __name__ == '__main__':

    CHAR_SET = string.ascii_lowercase + string.ascii_uppercase + string.digits
    #CHAR_COUNT_MAX = 10
    OUT_PATH = 'output'
    
    reset_dir(OUT_PATH)

    image_captcha = ImageCaptcha(fonts=['tests/Vera.ttf'])
    
    for _ in range(100):
        text_len = random.randint(10,20)
        text = ''.join(random.choice(CHAR_SET) for _ in range(text_len))

        output_fn = os.path.join(OUT_PATH,'{}.png'.format(text))

        image_captcha.write(text, output_fn)
