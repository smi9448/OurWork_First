from dataclasses import dataclass
import struct
import win32api
import win32gui
import win32con
import win32ui

m_lineColor = win32api.RGB(0, 0, 0)
m_lineWidth = 0
m_lineType = 0

class SPoint:
    x: float = None                     # X coordinate
    y: float = None                     # Y coordinate

class SMultiPoint:
    Box_Xmin: float = None
    Box_Ymin: float = None
    Box_Xmax: float = None
    Box_Ymax: float = None              # Bounding Box
    NumPoints: float = None             # NumPoints
    Points = []                         # The Points in the Set

class SPolyObject:
    Box_Xmin: float = None
    Box_Ymin: float = None
    Box_Xmax: float = None
    Box_Ymax: float = None              # Bounding Box
    NumParts: int = None                # Number of Parts
    NumPoints: int = None               # Total Number of Points
    Parts = []                          # Index to First Point in Part
    Points = []                         # Points for All Parts

class MainFileHeader:
    FileCode: int = None
    FileLength: int = None
    Version: int = None
    ShapeType: int = None
    Box_Xmin: float = None
    Box_Ymin: float = None
    Box_Xmax: float = None
    Box_Ymax: float = None

class RecordHeader:
    RecNum: int = None
    ContLen: int = 0

class CSHP:
    MainFileHdr = MainFileHeader()
    RecordHdr = []
    Point = []
    MultiPoint = []
    PolyObject = []
    m_nRecords: int = None

def FileOpen():
    hshp = open('C:/Users/smi23/OneDrive/바탕 화면/NGII_DTM_V2_5000/37608085/A0053326.shp', 'rb')
    hshx = open('C:/Users/smi23/OneDrive/바탕 화면/NGII_DTM_V2_5000/37608085/A0053326.shx', 'rb')
    tempBytes = hshp.read(4)
    SHPFile.MainFileHdr.FileCode = int.from_bytes(tempBytes, byteorder='big')
    #print(SHPFile.MainFileHdr.FileCode), 9994

    hshp.seek(24)

    tempBytes = hshp.read(4)
    SHPFile.MainFileHdr.FileLength = int.from_bytes(tempBytes, byteorder='big')
    #print(SHPFile.MainFileHdr.FileLength), 332272

    tempBytes = hshp.read(4)
    SHPFile.MainFileHdr.Version = int.from_bytes(tempBytes, byteorder='little')
    #print(SHPFile.MainFileHdr.Version), 1000
    
    tempBytes = hshp.read(4)
    SHPFile.MainFileHdr.ShapeType = int.from_bytes(tempBytes, byteorder='little')
    #print(SHPFile.MainFileHdr.ShapeType), 5

    tempBytes = hshp.read(8)
    SHPFile.MainFileHdr.Box_Xmin = (struct.unpack('d', tempBytes))[0]
    
    tempBytes = hshp.read(8)
    SHPFile.MainFileHdr.Box_Ymin = (struct.unpack('d', tempBytes))[0]

    tempBytes = hshp.read(8)
    SHPFile.MainFileHdr.Box_Xmax = (struct.unpack('d', tempBytes))[0]

    tempBytes = hshp.read(8)
    SHPFile.MainFileHdr.Box_Ymax = (struct.unpack('d', tempBytes))[0]

    hshx.seek(24)
    tempBytes = hshx.read(4)
    tempFilelen = 2 * int.from_bytes(tempBytes, byteorder='big')
    SHPFile.m_nRecords = int((tempFilelen-100) / 8)

    for _ in range(SHPFile.m_nRecords):
        SHPFile.RecordHdr = [RecordHeader]*SHPFile.m_nRecords

    if SHPFile.MainFileHdr.ShapeType == 1: # Point
        SHPFile.Point = [SPoint] * SHPFile.m_nRecords
    
        for i in range(SHPFile.m_nRecords):
            hshx.seek(100 + i * 8)
            tempBytes = hshx.read(4)
            offset = int.from_bytes(tempBytes, byteorder='big')
            offset *= 2

            hshp.seek(offset + 12)
            
            tempBytes = hshp.read(8)
            SHPFile.Point[i].x = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(8)
            SHPFile.Point[i].y = (struct.unpack('d', tempBytes))[0]

    elif SHPFile.MainFileHdr.ShapeType == 3 or SHPFile.MainFileHdr.ShapeType == 5: # Polyline or Polygon
        SHPFile.PolyObject = [SPolyObject] * SHPFile.m_nRecords

        for i in range(SHPFile.m_nRecords):
            hshx.seek(100 + i * 8)
            tempBytes = hshx.read(4)
            offset = int.from_bytes(tempBytes, byteorder='big')
            offset *= 2

            hshp.seek(offset + 12)

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Xmin = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Ymin = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Xmax = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Ymax = (struct.unpack('d', tempBytes))[0]
            
            tempBytes = hshp.read(4)
            SHPFile.PolyObject[i].NumParts = int.from_bytes(tempBytes, byteorder='little')

            tempBytes = hshp.read(4)
            SHPFile.PolyObject[i].NumPoints = int.from_bytes(tempBytes, byteorder='little')

            SHPFile.PolyObject[i].Parts = [int] * SHPFile.PolyObject[i].NumParts
            for j in range(SHPFile.PolyObject[i].NumParts):
                tempBytes = hshp.read(4)
                SHPFile.PolyObject[i].Parts[j] = int.from_bytes(tempBytes, byteorder='little')
  
            SHPFile.PolyObject[i].Points = [SPoint] * SHPFile.PolyObject[i].NumPoints
            for j in range(SHPFile.PolyObject[i].NumPoints):
                tempBytes = hshp.read(8)
                SHPFile.PolyObject[i].Points[j].x = (struct.unpack('d', tempBytes))[0]
                tempBytes = hshp.read(8)
                SHPFile.PolyObject[i].Points[j].y = (struct.unpack('d', tempBytes))[0]

    elif SHPFile.MainFileHdr.ShapeType == 8: # MultiPoint
        SHPFile.MultiPoint = [SMultiPoint] * SHPFile.m_nRecords

        for i in range(SHPFile.m_nRecords):
            hshx.seek(100 + i * 8)
            tempBytes = hshx.read(4)
            offset = int.from_bytes(tempBytes, byteorder='big')
            offset *= 2
            
            hshp.seek(offset + 12)

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Xmin = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Ymin = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Xmax = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(8)
            SHPFile.PolyObject[i].Box_Ymax = (struct.unpack('d', tempBytes))[0]

            tempBytes = hshp.read(4)
            SHPFile.MultiPoint[i].NumPoints = int.from_bytes(tempBytes, byteorder='little')

            SHPFile.MultiPoint[i].Points = [SPoint] * SHPFile.MultiPoint[i].NumPoints
            for _ in range(SHPFile.MultiPoint[i].NumPoints):
                tempBytes = hshp.read(8)
                SHPFile.MultiPoint[i].Points[j].x = (struct.unpack('d', tempBytes))[0]
                tempBytes = hshp.read(8)
                SHPFile.MultiPoint[i].Points[j].y = (struct.unpack('d', tempBytes))[0]
    
    hshx.close()
    hshp.close()

hWnd = win32gui.GetDesktopWindow()
hdc = win32gui.GetDC(hWnd)

def Draw():
    if SHPFile.MainFileHdr.ShapeType == 1: # Point
        DrawPoint()
    elif SHPFile.MainFileHdr.ShapeType == 3: # Polyline
        DrawPolyline()
    elif SHPFile.MainFileHdr.ShapeType == 5: # Polygon
        DrawPolygon()
    elif SHPFile.MainFileHdr.ShapeType == 8: # MultiPoint
        DrawMultiPoint()
    
def DrawPoint():
    pen = win32gui.CreatePen(m_lineType, m_lineWidth, m_lineColor)
    brush = win32gui.CreateSolidBrush(m_lineColor)

    savedDC = win32gui.SaveDC(hdc)

    win32gui.SelectObject(hdc, pen)
    win32gui.SelectObject(hdc, brush)

    for i in range(SHPFile.m_nRecords):
        win32gui.Ellipse(SHPFile.Point[i].x-2, SHPFile.Point[i].y-2, SHPFile.Point[i].x+2, SHPFile.Point[i].y+2)

    win32gui.RestoreDC(savedDC)

def DrawPolyline():
    savedDC = win32gui.SaveDC(hdc)

    pen = win32gui.CreatePen(m_lineType, m_lineWidth, m_lineColor)
    win32gui.SelectObject(hdc, pen)

    for i in range(SHPFile.m_nRecords):
        pScrPoints = [SPoint] * SHPFile.PolyObject[i].NumPoints
        pParts = [int] * SHPFile.PolyObject[i].NumParts

        for j in range(SHPFile.PolyObject[i].NumParts):
            if (j == SHPFile.PolyObject[i].NumParts - 1):
                pParts[j] = SHPFile.PolyObject[i].NumPoints - SHPFile.PolyObject[i].Parts[j]
            else:
                pParts[j] = SHPFile.PolyObject[i].Parts[j+1] - SHPFile.PolyObject[i].Parts[j]
        win32gui.PolyPolyline(pScrPoints, pParts, SHPFile.PolyObject[i].NumParts)

    win32gui.RestoreDC(savedDC)

def DrawPolygon():
    savedDC = win32gui.SaveDC(hdc)
    pen = win32gui.CreatePen(m_lineType, m_lineWidth, m_lineColor)
    brush = win32gui.CreateSolidBrush(m_lineColor)

    win32gui.SelectObject(hdc, brush)
    win32gui.SelectObject(hdc, pen)

    for i in range(SHPFile.m_nRecords):
        pScrPoints = [SPoint] * SHPFile.PolyObject[i].NumPoints
        pParts = [int] * SHPFile.PolyObject[i].NumParts

        for j in range(SHPFile.PolyObject[i].NumParts):
            if (j == SHPFile.PolyObject[i].NumParts - 1):
                pParts[j] = SHPFile.PolyObject[i].NumPoints - SHPFile.PolyObject[i].Parts[j]
            else:
                pParts[j] = SHPFile.PolyObject[i].Parts[j+1] - SHPFile.PolyObject[i].Parts[j]
            win32gui.Polygon(hdc, SHPFile.PolyObject[i].Points[j])
    
    win32gui.RestoreDC(savedDC)

def DrawMultiPoint():
    savedDC = win32gui.SaveDC(hdc)
    pen = win32gui.CreatePen(m_lineType, m_lineWidth, m_lineColor)

    win32gui.SelectObject(hdc, pen)

    for i in range(SHPFile.m_nRecords):
        pScrPoints = [SPoint] * SHPFile.PolyObject[i].NumPoints
        
        for j in range(SHPFile.PolyObject[i].NumPoints):
            win32gui.Ellipse(SHPFile.Point[i].x-2, SHPFile.Point[i].y-2, SHPFile.Point[i].x+2, SHPFile.Point[i].y+2)

    win32gui.RestoreDC(savedDC)

SHPFile = CSHP()
FileOpen()
Draw()


