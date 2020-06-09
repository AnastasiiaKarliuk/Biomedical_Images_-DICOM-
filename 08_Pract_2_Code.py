from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import dicom


class Image:
    def __init__(self, name):
        self.ds = dicom.read_file(name)
        self.bits = self.ds[0x280100].value
        self.data_type = self.image_type()
        self.image_pixels = self.normalize(self.ds.pixel_array)
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value
        self.normalised = False
        self.inversion = False
        self.x_pos = 0
        self.y_pos = 0

    def image_type(self):
        intercept = self.ds[0x281052].value
        slope = self.ds[0x281053].value
        if intercept != 0 and slope != 1:
            return GL_FLOAT
        else:
            return GL_UNSIGNED_BYTE if self.bits == 8 else GL_UNSIGNED_SHORT

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw()

    def draw(self):
        pixels_to_draw = np.copy(self.image_pixels)
        if self.normalised:
            pixels_to_draw = self.make_normalization(pixels_to_draw, 0.7, 1)
        if self.inversion:
            pixels_to_draw = self.make_inversion(pixels_to_draw)

        self.drawTexture(pixels_to_draw)
        self.define_coord(pixels_to_draw)
        glutSwapBuffers()

    def normalize(self, pixels):
        min, max = pixels.min(), pixels.max()
        new_min, new_max = 0, np.iinfo(pixels.dtype).max
        arr = (pixels - min)/(max - min)*(new_max - new_min)+new_min
        return arr.astype(int)

    def define_coord(self, pixels_to_draw):
        x = self.x_pos
        y = self.height - self.y_pos
        text = self.getPixelData(pixels_to_draw, x, y)
        self.printText(x, y, GLUT_BITMAP_9_BY_15, text)

    def make_normalization(self, pixels, p_min, p_max):
        p_min, p_max = p_min*pixels.max(), p_max*pixels.max()
        norm = p_min + (pixels - pixels.min())/(pixels.max() - pixels.min())*(p_max-p_min)
        return norm.astype(int)

    def make_inversion(self, pixels):
        inv = pixels.max() - pixels + pixels.min()
        return inv

    def drawTexture(self, data):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.height, 0, GL_LUMINANCE, self.data_type, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(0.0, 0.0)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(self.width, 0.0)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(self.width, self.height)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(0.0, self.height)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def getPixelData(self, pixels, y, x):
        return str(pixels[x][y]) if (0 < x < self.width) and (0 < y < self.height) else ''

    def printText(self, x, y, font, text):
        glColor3f(1, 1, 1)
        glRasterPos2d(x, y)
        for c in text:
            glutBitmapCharacter(font, ctypes.c_int(ord(c)))

    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        if key == 'i':
            self.inversion = not self.inversion
        if key == 'n':
            self.normalised = not self.normalised
        self.display()

    def onMotion(self, x, y):
        self.y_pos = y
        self.x_pos = x
        self.display()


def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('Lab_2 Var_8')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

    image = Image("Data-Pract/Lab#2-#6 - DICOM_single_16bits/DICOM_Image_16b.dcm")
    initWindow(image.width, image.height)
    image.init()

    glutDisplayFunc(image.display)
    glutKeyboardFunc(image.keyPressed)
    glutPassiveMotionFunc(image.onMotion)
    glutMainLoop()


if __name__ == '__main__':
    main()