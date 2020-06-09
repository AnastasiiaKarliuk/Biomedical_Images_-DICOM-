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
        gluOrtho2D(-self.width, self.width, -self.height, self.height)
        # glMatrixMode(GL_MODELVIEW)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.draw()

    def draw(self):
        pixels_to_draw = np.copy(self.image_pixels)
        self.drawTexture(pixels_to_draw)
        glutSwapBuffers()

    def normalize(self, pixels):
        min, max = pixels.min(), pixels.max()
        new_min, new_max = 0, np.iinfo(pixels.dtype).max
        arr = (pixels - min)/(max - min)*(new_max - new_min)+new_min
        return arr.astype(int)

    def drawTexture(self, data):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.width, self.height, 0, GL_LUMINANCE, self.data_type, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex2d(-self.width/2, -self.height/2)
        glTexCoord2d(1.0, 0.0)
        glVertex2d(self.width/2, -self.height/2)
        glTexCoord2d(1.0, 1.0)
        glVertex2d(self.width/2, self.height/2)
        glTexCoord2d(0.0, 1.0)
        glVertex2d(-self.width/2, self.height/2)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def keyPressed(self, bkey, x, y):
        key = unicode(bkey, errors='ignore')
        if key == '1':
            xp = int(input('Enter the X (for mirror): '))
            matrix = np.array([-1, 0, 0, 0,
                                0, 1, 0, 0,
                                0, 0, 1, 0,
                                2*xp, 0, 0, 1])
            glMultMatrixf(matrix)
        elif key == '2':
            Sx = float(input('Scaling coef Sx : '))
            Sy = float(input('Scaling coef Sy : '))
            matrix = np.array([Sx, 0, 0, 0,
                                0, Sy, 0, 0,
                                0, 0, 1, 0,
                                0, 0, 0, 1])
            glMultMatrixf(matrix)
        elif key == '3':
            xp = int(input('Enter the X (for mirror): '))
            matrix1 = np.array([[-1, 0, 0, 0],
                               [0, 1, 0, 0],
                               [0, 0, 1, 0],
                               [2 * xp, 0, 0, 1]])
            Sx = float(input('Scaling coef Sx : '))
            Sy = float(input('Scaling coef Sy : '))
            matrix2 = np.array([[Sx, 0, 0, 0],
                               [0, Sy, 0, 0],
                               [0, 0, 1, 0],
                               [0, 0, 0, 1]])
            glMultMatrixf(matrix1 @ matrix2)
        elif key == '4':
            glLoadIdentity()
        self.display()


def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('Lab_6 Var_8')


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

    image = Image("Data-Pract/Lab#2-#6 - DICOM_single_16bits/DICOM_Image_16b.dcm")
    initWindow(image.width*2, image.height*2)
    image.init()

    glutDisplayFunc(image.display)
    glutKeyboardFunc(image.keyPressed)
    glutMainLoop()


if __name__ == '__main__':
    main()
