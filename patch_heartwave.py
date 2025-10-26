# patch_heartwave.py
from PyQt5 import QtGui, QtCore, QtWidgets
import numpy as np
import heartwave.util as util
import heartwave.widgets as hw

def _patched_draw(self, im, persons):
    """Safe draw: cast to int, avoid numpy.float64 to QPainter overload mismatch."""
    qim = util.qImage(im)
    p = QtGui.QPainter(qim)
    try:
        for person in persons:
            x, y, w, h = person.face
            # 强制转 int，且用整数除法
            x, y, w, h = int(x), int(y), int(w), int(h)

            p.setPen(QtGui.QColor(255, 255, 255, 64))
            p.drawRect(x, y, w, h // 4)

            # 文字（BPM）也确保是 int，避免类型再出问题
            font = p.font()
            font.setPixelSize(28)
            p.setFont(font)
            p.setPen(QtGui.QColor(255, 255, 255))

            bpm_seq = getattr(person, "bpm", [])
            bpm = int(bpm_seq[-1]) if bpm_seq else 0
            p.drawText(x, y, w, h, QtCore.Qt.AlignHCenter, '♡' + str(bpm))
    finally:
        p.end()

    self.image = qim
    self.setMinimumSize(qim.size())
    self.update()

# 替换 heartwave.widgets.View.draw
hw.View.draw = _patched_draw
