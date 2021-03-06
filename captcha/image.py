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
import math

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

        self._enable_back_text = True
        self._enable_background_noise = True
        self._enable_noise_bg = True
        self._enable_noise_dot = True
        self._enable_noise_curve = True
        self._enable_panda = False

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
    def create_noise_dots(image, color, width=3, number=30):
        draw = Draw(image)
        w, h = image.size
        for _ in range(number):
            xx = random.randint(1,width)
            yy = random.randint(1,width)
            x = random.randint(0, w-xx)
            y = random.randint(0, h-yy)
            draw.ellipse(((x,y), (x+xx,y+yy)), fill=color if rand_bool() else random_color())
        return image

    def create_captcha_background(self, background_avoid):
        """Create the CAPTCHA background.

        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        chunk_max = max(1,int(max(self._width, self._height)/10)) if self._enable_background_noise else 1
        chunk = random.randint(1,chunk_max), random.randint(1,chunk_max)
        image = Image.new('RGB', chunk, (0,0,0))
        draw = Draw(image)
        for x in range(chunk[0]):
            for y in range(chunk[1]):
                color = random_color(background_avoid,64) if not self._enable_panda else (0,0,0,255)
                draw.point((x,y),color)
        big_side = math.ceil((self._width*self._width+self._height*self._height)**0.5)+4
        image = image.resize((big_side, big_side),random.choice([Image.NEAREST,Image.BILINEAR]))
        image = image.rotate(random.random()*360, random.choice([Image.NEAREST,Image.BILINEAR]))
        crop_x0 = int((big_side-self._width)/2)
        crop_y0 = int((big_side-self._height)/2)
        crop_x1 = crop_x0 + self._width
        crop_y1 = crop_y0 + self._height
        image = image.crop((crop_x0,crop_y0,crop_x1,crop_y1))
        return image

    def create_captcha_text(self, image, chars, color, back_color=None, back_color_count=0, back_radius=0):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        if len(chars) <= 0:
            return image
        
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
            im = im.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=max(im.size))
            #im = im.crop(im.getbbox())

            # warp
            w, h = im.size
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
            im = im.crop(im.getbbox())
            return im

        images = []
        for c in chars:
            images.append(_draw_character(c))

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        rand = int(0.35 * average)
        offset0 = int(average * 0.1)

        neg_off_list = [ random.randint(-rand, 0) for _ in images ]
        y_max_list = [ self._height-im.size[1] for im in images ]
        y_list = [ (random.randint(0,y) if (y >= 0) else int(y/2)) for y in y_max_list ]
        offset0_max = max(0,width-text_width-sum(neg_off_list[:-1])-offset0*2)
        offset0 += random.randint(0,offset0_max)

        for _ in range(back_color_count):
            xs,ys = tuple(int(i*back_radius) for i in random_vector(2))
            offset=offset0
            for im, neg_off, y in zip(images,neg_off_list,y_list):
                w, h = im.size
                #mask = im.convert('L').point(table)
                rgb_img = Image.new('RGB', im.size, back_color)
                mask = im
                image.paste(rgb_img, (offset+xs, y+ys), mask)
                offset = offset + w + neg_off

        offset=offset0
        for im, neg_off, y in zip(images,neg_off_list,y_list):
            w, h = im.size
            #mask = im.convert('L').point(table)
            rgb_img = Image.new('RGB', im.size, color)
            mask = im
            image.paste(rgb_img, (offset, y), mask)
            offset = offset + w + neg_off

        if width != self._width:
            image = image.resize((self._width, self._height))
        
        return image

    def generate_image(self, chars):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        """
        color = random_color() if not self._enable_panda else (255,255,255,255)
        back_color = random_color(color,64) if not self._enable_panda else (0,0,0,255)
        back_color_count = random.randint(1,10) if (self._enable_back_text and rand_bool()) else 0
        background_avoid_color = color if back_color_count == 0 else None
        dot_count   = random.randint(0,40) if self._enable_noise_dot else 0
        curve_count = random.randint(0,10) if self._enable_noise_curve else 0
        
        im = self.create_captcha_background(background_avoid_color)
        im = self.create_captcha_text(im, chars, color, back_color, back_color_count, 5)
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

def random_vector(ndim):
    while True:
        ret = tuple((random.random()*2-1) for _ in range(ndim))
        norm2 = sum((r*r) for r in ret)
        if norm2 <= 1:
            return ret
