from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import dicom
import operator
import pickle
from pprint import pprint


class Image:
    def __init__(self, name):
        self.ds = dicom.read_file(name)
        self.bits = self.ds[0x280100].value
        self.data_type = self.image_type()
        self.image_pixels = self.normalize(self.ds.pixel_array)
        self.width, self.height = self.ds[0x280010].value, self.ds[0x280011].value
        self.filtered = False

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
        if self.filtered:
            pixels_to_draw = self.make_filtration(pixels_to_draw)
        self.drawTexture(pixels_to_draw)
        glutSwapBuffers()

    def make_filtration(self, pixels):
        hist = {key: (pixels == key).sum() for key in range(pixels.min(), pixels.max())}
        li = np.array(list(hist.values()))
        pmin, pmax =np.where(li==np.min(li[np.nonzero(li)]))[0][0], int(np.argmax(li))

        x = [el for el in reversed(range(pmax, pmin+1, 1))]
        dist = {key: self.distance(pmin, pmax, key, hist[pmin], hist[pmax], hist[key]) for key in x}
        tresh = max(dist.items(), key=operator.itemgetter(1))[0]

        mask = np.copy(pixels)
        mask[mask < tresh] = 0
        mask[mask >= tresh] = np.iinfo(pixels.dtype).max
        table = [{'x': x, 'y': y, 'mask': mask[x, y], 'value': pixels[x, y]}
                 for x in range(pixels.shape[0]) for y in range(pixels.shape[1])]
        self.save(table)
        pprint(table)
        return mask

    def save(self, data):
        with open('filename.pickle', 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def distance(self, x1, x2, x3, y1, y2, y3):
        A, B, C = self.line(x1, x2, y1, y2)
        dist = np.abs(A*x3 + B*y3 + C)/np.sqrt(A**2 + B**2)
        return dist

    def line(self, x1, x2, y1, y2):
        A = y2 - y1
        B = -(x2 - x1)
        C = -x1*(y2 - y1) + y2*(x2 - x1)
        return A, B, C

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
        if key == 'f':
            self.filtered = not self.filtered
        self.display()

    def onMotion(self, x, y):
        self.display()


def initWindow(width, height):
    glutInitWindowSize(width, height)
    glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) // 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) // 2)
    glutCreateWindow('Lab_4 Var_8')


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
