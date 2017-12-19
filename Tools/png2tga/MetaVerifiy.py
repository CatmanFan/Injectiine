import struct
import msvcrt as m
import os

def wait():
    m.getch()
    
def readByte(file):
    return struct.unpack("B", file.read(1))[0]
 
def readu16le(file):
    return struct.unpack("<H", file.read(2))[0]
 
def readu32le(file):
    return struct.unpack("<I", file.read(4))[0]


tgas = ["iconTex.tga","bootLogoTex.tga","bootDrcTex.tga","bootTvTex.tga"]
dimensions = [[128,128,32],[170,42,32],[854,480,24],[1280,720,24]]
for i in range(len(tgas)):
    tga = tgas[i]
    dimension = dimensions[i]
    if os.path.exists(tga):
        with open(tga,"rb+") as f:
            header = readu32le(f)
            if header != 0x00020000:
                print tga + "is compressed. it cant be compressed!"
                break
            f.seek(12)
            actDimensions = [readu16le(f),readu16le(f),readByte(f)]
            hasHadBadDiment = False
            for j in range(len(actDimensions)):
                if j == 0:
                    type = "width"
                elif j == 1:
                    type = "height"
                else:
                    type = "depth"
                diment = dimension[j]
                actDiment = actDimensions[j]
                if diment != actDiment:
                    if not hasHadBadDiment:
                        hasHadBadDiment = True
                        print "dimensions are not valid for: " + tga
                    print type + " is: " + str(actDiment) + " should be: " + str(diment)
            if hasHadBadDiment:
                break
            f.seek(1,1)
            f.seek(actDimensions[0]*actDimensions[1]*(actDimensions[2]/8),1)
            f.write("\x00\x00\x00\x00\x00\x00\x00\x00TRUEVISION-XFILE\x2E\x00")
    else:
        print tga + " could not be found!"
print "All TGA's verified!"
print "press any key to exit..."
#todo verifiy bootovie.h264
wait()        
        
