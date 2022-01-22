import cv2
import gzip
import numpy as np
# http://yann.lecun.com/exdb/mnist/, https://storage.googleapis.com/cvdf-datasets/mnist/

class MnistData():
    def __init__(self, dataPath, isOneHot = False):
        with open(dataPath+'train-images-idx3-ubyte.gz', 'rb') as f:
            self.trainImage = self.extractImage(f)
        with open(dataPath+'train-labels-idx1-ubyte.gz', 'rb') as f:
            self.trainLabel = self.extractLabel(f)
        with open(dataPath+'t10k-images-idx3-ubyte.gz', 'rb') as f:
            self.testImage  = self.extractImage(f)
        with open(dataPath+'t10k-labels-idx1-ubyte.gz', 'rb') as f:
            self.testLabel  = self.extractLabel(f, isOneHot=isOneHot)

        self.isOneHot = isOneHot
        if self.isOneHot:
            self.trainLabel = self.convertToOneHot(self.trainLabel)
            self.testLabel  = self.convertToOneHot(self.testLabel)
        else:
            self.trainLabel = self.trainLabel.astype(np.float32)
            self.testLabel  = self.testLabel.astype(np.float32)

    def getBatch(self, batchSize, isTrain):
        if isTrain:
            index = np.random.choice(len(self.trainImage), batchSize, True)
            return self.trainImage[index], self.trainLabel[index]
        else:
            index = np.random.choice(len(self.testImage), batchSize, True)
            return self.testImage[index], self.testLabel[index]

    def read4Byte(self, byteStream):
        dt = np.dtype(np.uint32).newbyteorder('>')
        return np.frombuffer(byteStream.read(4), dtype=dt)[0]

    def extractImage(self, f):
        print('Extracting', f.name)
        with gzip.GzipFile(fileobj=f) as byteStream:
            if self.read4Byte(byteStream) != 2051:
                raise ValueError("Failed reading file!")
            nImage  = self.read4Byte(byteStream)
            rows    = self.read4Byte(byteStream)
            cols    = self.read4Byte(byteStream)
            buf     = byteStream.read(rows * cols * nImage)
            return np.frombuffer(buf, dtype = np.uint8).astype(np.float32).reshape(nImage, rows, cols, 1)/255

    def extractLabel(self, f, isOneHot=False, nClass=10):
        print('Extracting', f.name)
        with gzip.GzipFile(fileobj=f) as byteStream:
            if self.read4Byte(byteStream) != 2049:
                raise ValueError("Failed reading file!")
            nLabel = self.read4Byte(byteStream)
            buf = byteStream.read(nLabel)
            return np.frombuffer(buf, dtype=np.uint8)

    def convertToOneHot(self, labelIndex, nClass=10):
        nLabel  = labelIndex.shape[0]
        res     = np.zeros((nLabel, nClass), dtype=np.float32)
        offset  = np.arange(nLabel) * nClass
        res.flat[offset + labelIndex] = 1
        return res

    def saveImage(self, count, outputPath, isTrain):
        if self.isOneHot:
            return
        image, label = ([self.testImage, self.testLabel],[self.trainImage, self.trainLabel])[isTrain]
        for i in range(min(count,10000)):
            cv2.imwrite(outputPath+str(i).zfill(5)+"-"+str(label[i])+".jpg", (image[i]*255).astype(np.uint8))
