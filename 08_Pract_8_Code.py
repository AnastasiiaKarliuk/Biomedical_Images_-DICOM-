from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import dicom
from os.path import join


class Image:
    def __init__(self, path):
        ds_ct = dicom.read_file(join(path, "2-ct.dcm"))
        ds_mri = dicom.read_file(join(path, "2-mri.dcm"))

        self.data_type = self.image_type(ds_ct)
        self.height, self.width = ds_mri[0x280010].value, ds_mri[0x280011].value
        self.d_height, self.d_width = 512, 256
        self.ct_pixels = np.zeros((self.d_height, self.d_width))
        self.mri_pixels = np.zeros((self.d_height, self.d_width))

        for i in range(self.height):
            for j in range(self.width):
                self.ct_pixels[i][j] = ds_ct.pixel_array[i][j]
                self.mri_pixels[i][j] = ds_mri.pixel_array[i][j]

    def image_type(self, ds):
            return GL_UNSIGNED_BYTE if ds[0x280100].value == 8 else GL_UNSIGNED_SHORT

    def init(self):
        glClearColor(0, 0, 0, 0.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0.0, 1.0, 0.0, 1.0)

    def doubled(self, first, second):
        result = np.copy(first)
        c = 1
        for i in range(self.height//2, self.height):
            for j in range(self.width):
                result[i][j] = second[i, j] if c == 2 else first[i, j]
                if c == 1:
                    c = 2
                else:
                    c = 1
        return result

    def display(self, key='d'):
        glClear(GL_COLOR_BUFFER_BIT)
        if key == 'c':
            pixels_to_draw = self.ct_pixels
        elif key == 'm':
            pixels_to_draw = self.mri_pixels
        elif key == 'd':
            pixels_to_draw = self.doubled(self.ct_pixels, self.mri_pixels)
        self.drawTexture(pixels_to_draw)
        glutSwapBuffers()

    def drawTexture(self, data):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.d_width, self.d_height, 0, GL_LUMINANCE, self.data_type, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(0, 0)
        glTexCoord2d(self.width/self.d_width, 0.0)
        glVertex2d(1.0, 0)
        glTexCoord2d(self.width/self.d_width, self.height/self.d_height)
        glVertex2d(1.0, 1.0)
        glTexCoord2d(0.0, self.height/self.d_height)
        glVertex2d(0.0, 1.0)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        self.display(key)


def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2,
                           (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('Lab_8 Var_8')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    path ="Data-Pract/Lab#8 - DICOM_fusion_8bits/Var1 - DICOM_8bits/"
    image = Image(path)
    initWindow(image.width, image.height)
    image.init()

    glutDisplayFunc(image.display)
    glutKeyboardFunc(image.keyPressed)
    glutMainLoop()

if __name__ == '__main__':
    main()
