from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import dicom

class Image:
    def __init__(self, name: str):
        self.ds = dicom.read_file(name)
        self.image_pixels = self.ds.pixel_array
        self.bits = self.ds[0x280100].value
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value
        self.isColorGreen = False
        self.isBackgroud = False

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw()

    def draw(self):
        type_texture = GL_LUMINANCE
        pixels_to_draw = np.copy(self.image_pixels)
        if self.isColorGreen:
            pixels_to_draw = self.get_color_channel(self.transform_gradient(pixels_to_draw))
            type_texture = GL_RGB
        if self.isBackgroud:
            pixels_to_draw = self.get_mask(pixels_to_draw)

        self.drawTexture(pixels_to_draw, type_texture)
        glutSwapBuffers()

    def get_mask(self, pixels):
        tril_matrix = np.tril_indices(self.height, 0, self. width)
        triu_matrix = np.triu_indices(self.height, 0, self.width)
        pixels[tril_matrix] = 0 & pixels[tril_matrix]
        pixels[triu_matrix] = 255 & pixels[triu_matrix]
        return pixels

    def transform_gradient(self, pixels):
        gradient = {}
        color = 0
        for key in range(pixels.max(), -1, -1):
            gradient[key] = color
            color += 2 if key >= 127 else -2

        vfunc = np.vectorize(lambda x: gradient[x])
        return vfunc(pixels)

    def get_color_channel(self, pixels):
        rgb = np.zeros((self.height, self.width, 3))
        rgb[:, :, 1] = pixels
        return rgb

    def drawTexture(self, data, type_):
        glTexImage2D(GL_TEXTURE_2D, 0, type_, self.width, self.height, 0, type_, GL_UNSIGNED_BYTE, data)
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

    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        if key == 'b':
            self.isBackgroud = not self.isBackgroud
        if key == 'c':
            self.isColorGreen = not self.isColorGreen
        self.display()

    def onMotion(self, x, y):
        self.display()


def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('Lab_1 Var_8')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

    image = Image("DICOM_Image_for_Lab_2.dcm")
    initWindow(image.width, image.height)
    image.init()

    glutDisplayFunc(image.display)
    glutKeyboardFunc(image.keyPressed)
    glutPassiveMotionFunc(image.onMotion)
    glutMainLoop()


if __name__ == '__main__':
    main()
