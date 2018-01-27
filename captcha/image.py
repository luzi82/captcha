# coding: utf-8
"""
    captcha.image
    ~~~~~~~~~~~~~

    Generate Image CAPTCHAs, just the normal image CAPTCHAs you are using.
"""

import os
import random
from PIL import Image
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
try:
    from wheezy.captcha import image as wheezy_captcha
except ImportError:
    wheezy_captcha = None

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]

if wheezy_captcha:
    __all__ = ['ImageCaptcha', 'WheezyCaptcha']
else:
    __all__ = ['ImageCaptcha']


table  =  []
for  i  in  range( 256 ):
    table.append( i * 1.97 )


class _Captcha(object):
    def generate(self, chars, format='png'):
        """Generate an Image Captcha of the given characters.

        :param chars: text to be generated.
        :param format: image file format
        """
        im = self.generate_image(chars)
        out = BytesIO()
        im.save(out, format=format)
        out.seek(0)
        return out

    def write(self, chars, output, format='png'):
        """Generate and write an image CAPTCHA data to the output.

        :param chars: text to be generated.
        :param output: output destination.
        :param format: image file format
        """
        im = self.generate_image(chars)
        return im.save(output, format=format)


class WheezyCaptcha(_Captcha):
    """Create an image CAPTCHA with wheezy.captcha."""
    def __init__(self, width=200, height=75, fonts=None):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS

    def generate_image(self, chars):
        text_drawings = [
            wheezy_captcha.warp(),
            wheezy_captcha.rotate(),
            wheezy_captcha.offset(),
        ]
        fn = wheezy_captcha.captcha(
            drawings=[
                wheezy_captcha.background(),
                wheezy_captcha.text(fonts=self._fonts, drawings=text_drawings),
                wheezy_captcha.curve(),
                wheezy_captcha.noise(),
                wheezy_captcha.smooth(),
            ],
            width=self._width,
            height=self._height,
        )
        return fn(chars)


class ImageCaptcha(_Captcha):
    """Create an image CAPTCHA.

    Many of the codes are borrowed from wheezy.captcha, with a modification
    for memory and developer friendly.

    ImageCaptcha has one built-in font, DroidSansMono, which is licensed under
    Apache License 2. You should always use your own fonts::

        captcha = ImageCaptcha(fonts=['/path/to/A.ttf', '/path/to/B.ttf'])

    You can put as many fonts as you like. But be aware of your memory, all of
    the fonts are loaded into your memory, so keep them a lot, but not too
    many.

    :param width: The width of the CAPTCHA image.
    :param height: The height of the CAPTCHA image.
    :param fonts: Fonts to be used to generate CAPTCHA images.
    :param font_sizes: Random choose a font size from this parameters.
    """
    def __init__(self, width=160, height=60, fonts=None, font_sizes=None):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS
        self._font_sizes = font_sizes or (42, 50, 56)
        self._truefonts = []

    def set_size(self, width, height):
        self._width = width
        self._height = height

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        return self._truefonts

    @staticmethod
    def create_noise_curve(image, color):
        w, h = image.size
        x1 = random.randint(0, int(w / 2))
        x2 = random.randint(w - int(w / 2), w)
        if rand_bool(): # down
            y1 = random.randint(0, int(h / 2))
            y2 = random.randint(h - int(h / 2), h)
            y1 += y1-y2
            end = random.randint(90, 180)
            start = random.randint(0, 90)
        else: # down
            y1 = random.randint(0, int(h / 2))
            y2 = random.randint(h - int(h / 2), h)
            y2 += y2-y1
            end = random.randint(270, 360)
            start = random.randint(180, 270)
        points = [x1, y1, x2, y2]
        Draw(image).arc(points, start, end, fill=color)
        return image

    @staticmethod
    def create_noise_dots(image, color, width=2, number=30):
        draw = Draw(image)
        w, h = image.size
        for _ in range(number):
            x = random.randint(0, w)
            y = random.randint(0, h)
            rx = random.randint(1,width)
            ry = random.randint(1,width)
            draw.ellipse(((x-rx,y-ry), (x+rx,y+ry)), fill=color if rand_bool() else random_color())
        return image

    def create_captcha_background(self, background):
        """Create the CAPTCHA background.

        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        image = Image.new('RGB', (self._width, self._height), background)
        return image

    def create_captcha_text(self, image, chars, color):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        draw = Draw(image)

        def _draw_character(c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font=font)

            dx = random.randint(0, 4)
            dy = random.randint(0, 6)
            im = Image.new('L', (w + dx, h + dy), 0)
            Draw(im).text((dx, dy), c, font=font, fill=255)

            # rotate
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=1)

            # warp
            dx = w * random.uniform(0.1, 0.3)
            dy = h * random.uniform(0.2, 0.3)
            x1 = int(random.uniform(-dx, dx))
            y1 = int(random.uniform(-dy, dy))
            x2 = int(random.uniform(-dx, dx))
            y2 = int(random.uniform(-dy, dy))
            w2 = w + abs(x1) + abs(x2)
            h2 = h + abs(y1) + abs(y2)
            data = (
                x1, y1,
                -x1, h2 - y2,
                w2 + x2, h2 + y2,
                w2 - x2, -y1,
            )
            im = im.resize((w2, h2))
            im = im.transform((w, h), Image.QUAD, data)
            return im

        images = []
        for c in chars:
            images.append(_draw_character(c))

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        rand = int(0.25 * average)
        offset = int(average * 0.1)

        neg_off_list = [ random.randint(-rand, 0) for _ in images ]
        offset_max = max(0,width-text_width-sum(neg_off_list[:-1])-offset*2)
        offset += random.randint(0,offset_max)

        for im, neg_off in zip(images,neg_off_list):
            w, h = im.size
            #mask = im.convert('L').point(table)
            rgb_img = Image.new('RGB', im.size, color)
            mask = im
            image.paste(rgb_img, (offset, int((self._height - h) / 2)), mask)
            offset = offset + w + neg_off

        if width != self._width:
            image = image.resize((self._width, self._height))
        
        return image

    def generate_image(self, chars):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        """
        background = random_color()
        color = random_color(background,64)
        #color = color[:-1] + (random.randint(128,255),)
        dot_count   = random.randint(0,40)
        curve_count = random.randint(0,10)
        
        im = self.create_captcha_background(background)
        im = self.create_captcha_text(im, chars, color)
        self.create_noise_dots(im, color, number=dot_count)
        for _ in range(curve_count):
            self.create_noise_curve(im, color if rand_bool() else random_color())
        if rand_bool():
            im = im.filter(ImageFilter.SMOOTH)
        return im


def random_color(avoid_color=None, min_radius=None):
    while(True):
        ret = (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255),255)
        if avoid_color is None:
            return ret
        diff = [a-b for a,b in zip(ret, avoid_color)]
        diff2 = [d*d for d in diff]
        radius2 = sum(diff2)
        if radius2 >= min_radius*min_radius:
            return ret

def rand_bool():
    return random.random()<0.5
