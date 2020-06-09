from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np
import dicom
import os


class Image:
    def __init__(self, name):
        self.n = len(os.listdir(name))

        image_pixels = []
        for i, file in enumerate(sorted(os.listdir(name))):
            ds = dicom.read_file(os.path.join(name, file))
            self.data_type = self.image_type(ds)
            image_pixels.append(self.normalize(ds.pixel_array))

        self.image_pixels = np.array(image_pixels)
        self.width, self.height = ds[0x280010].value, ds[0x280011].value
        self.slice = ds[0x180050].value
        self.space = ds[0x180088].value

        self.front_pixels = np.zeros((self.height, self.n, self.width))
        for i in range(self.height):
            for j in range(self.n):
                for k in range(self.width):
                    self.front_pixels[i][j][k] = self.image_pixels[j][i][k]

        self.sag_pixels = np.zeros((self.width, self.n, self.height))
        for i in range(self.width):
            for j in range(self.n):
                for k in range(self.height):
                    self.sag_pixels[i][j][k] = self.image_pixels[j][k][i]

        self.cor_layer, self.sag_layer, self.front_layer = 0, 0, 0

    def image_type(self, ds):
        intercept = ds[0x281052].value
        slope = ds[0x281053].value
        if intercept != 0 and slope != 1:
            return GL_FLOAT
        else:
            return GL_UNSIGNED_BYTE if ds[0x280100].value == 8 else GL_UNSIGNED_SHORT

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glRotatef(-45, 1, 0, 0)
        glRotatef(45, 0, 0, 1)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw()

    def printText(self, x, y, z, font, text):
        glRasterPos3f(x, y, z)
        for c in text:
            glutBitmapCharacter(font, ctypes.c_int(ord(c)))

    def drawAxis(self):
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        glVertex3f(-2.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)
        glVertex3f(0.0, -2.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        glVertex3f(0.0, 0.0, -2.0)
        glVertex3f(0.0, 0.0, 2.0)
        glEnd()
        self.printText(-1.2, 0.05, 0, GLUT_BITMAP_HELVETICA_18, "x")
        self.printText(0.05, -1.2, 0, GLUT_BITMAP_HELVETICA_18, "y")
        self.printText(0.05, 0, 0.9, GLUT_BITMAP_HELVETICA_18, "z")

    def draw(self):
        self.drawAxis()
        self.drawTexture()
        glutSwapBuffers()

    def normalize(self, pixels):
        min, max = pixels.min(), pixels.max()
        new_min, new_max = 0, np.iinfo(pixels.dtype).max
        arr = (pixels - min)/(max - min)*(new_max - new_min)+new_min
        return arr.astype(int)

    def drawTexture(self):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.height, self.width, 0,
                     GL_LUMINANCE, self.data_type, self.image_pixels[self.cor_layer])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, self.cor_layer*(self.slice+self.space)/self.height)
        glTexCoord2f(1, 0)
        glVertex3f(1, 0, self.cor_layer*(self.slice+self.space)/self.height)
        glTexCoord2f(1, 1)
        glVertex3f(1, 1, self.cor_layer*(self.slice+self.space)/self.height)
        glTexCoord2f(0, 1)
        glVertex3f(0, 1, self.cor_layer*(self.slice+self.space)/self.height)
        glEnd()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.n, 0,
                     GL_LUMINANCE, self.data_type, self.sag_pixels[self.sag_layer])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(self.sag_layer/self.height, 0, 0)
        glTexCoord2f(1, 0)
        glVertex3f(self.sag_layer/self.height, 1, 0)
        glTexCoord2f(1, 1)
        glVertex3f(self.sag_layer/self.height, 1, self.n*(self.slice+self.space)/self.height)
        glTexCoord2f(0, 1)
        glVertex3f(self.sag_layer/self.height, 0, self.n*(self.slice+self.space)/self.height)
        glEnd()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.n, 0,
                     GL_LUMINANCE, self.data_type, self.front_pixels[self.front_layer])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, self.front_layer/self.height, 0)
        glTexCoord2f(1, 0)
        glVertex3f(1, self.front_layer/self.height, 0)
        glTexCoord2f(1, 1)
        glVertex3f(1, self.front_layer/self.height, self.n*(self.slice+self.space)/self.height)
        glTexCoord2f(0, 1)
        glVertex3f(0, self.front_layer/self.height, self.n*(self.slice+self.space)/self.height)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glFlush()

    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        if key == "t":
            matrix = np.array([1, 0, 0, 0,
                               0, -1, 0, 0,
                               0, 0, 1, 0,
                               0, 0, 0, 1])
            glMultMatrixf(matrix)
        elif key == "w" and self.cor_layer < self.n-1:
            self.cor_layer += 1
        elif key == "s" and self.cor_layer > 0:
            self.cor_layer -= 1
        elif key == "d" and self.sag_layer < self.width-1:
            self.sag_layer += 1
        elif key == "a" and self.sag_layer > 0:
            self.sag_layer -= 1
        elif key == "z" and self.front_layer < self.height-1:
            self.front_layer += 1
        elif key == "c" and self.front_layer > 0:
            self.front_layer -= 1
        self.display()


def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2,
                           (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('Lab_7 Var_8')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    path ="Data-Pract/Lab#7 - DICOM_set_16bits"
    image = Image(path)
    initWindow(image.width*2, image.height*2)
    image.init()

    glutDisplayFunc(image.display)
    glutKeyboardFunc(image.keyPressed)
    glutMainLoop()


if __name__ == '__main__':
    main()
