import PyQt5.Qt as qt
import numpy as np

from heartwave.plot import Plot
import heartwave.util as util


class View(qt.QWidget):
    """
    Video canvas with overlay.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.image = None

    def draw(self, im, persons):
        """
        Display the CV2 image with overlay from the analysed persons.
        """
        qim = util.qImage(im)
        with qt.QPainter(qim) as p:
            for person in persons:
                # ---- face box: ensure ints ----
                x, y, w, h = person.face
                x, y, w, h = int(x), int(y), int(w), int(h)

                p.setPen(qt.QColor(255, 255, 255, 64))
                # 使用整数除法，避免传 float
                p.drawRect(x, y, w, h // 4)
                # 如果还想画第二个小框，注意也要是整数：
                # p.drawRect(x, y + h // 2, w, h // 4)

                # ---- text: BPM ----
                font = p.font()
                font.setPixelSize(28)
                p.setFont(font)
                p.setPen(qt.QColor(255, 255, 255))
                bpm = int(person.bpm[-1]) if getattr(person, "bpm", None) and len(person.bpm) else 0
                p.drawText(x, y, w, h, qt.Qt.AlignHCenter, '♡' + str(bpm))

        self.image = qim
        self.setMinimumSize(qim.size())
        self.update()

    def paintEvent(self, ev):
        if self.image:
            with qt.QPainter(self) as p:
                p.drawImage(0, 0, self.image)


class CurveWidget(qt.QSplitter):
    """
    Realtime curves.
    """
    def __init__(self, parent=None):
        super().__init__(qt.Qt.Vertical, parent=parent)
        self.setMinimumHeight(640)

        # 五个子图：Signal / Filtered / Spectrum / BPM / Blood Pressure
        titles = ('Signal', 'Filtered', 'Spectrum', 'BPM', 'Blood Pressure')
        self.plots = [Plot(title=t) for t in titles]
        for plot in self.plots:
            self.addWidget(plot)

        # 预创建曲线句柄：每个子图最多两条（如 BPM + 平滑均值）
        self._curves = {
            'raw': None,
            'filtered': None,
            'spectrum': None,  # 频谱需要 x 轴
            'bpm': None,
            'bpm_avg': None,
            'bp': None,
        }

    @staticmethod
    def _finite(arr):
        if arr is None:
            return np.array([], dtype=float)
        a = np.asarray(arr, dtype=float)
        if a.ndim == 0:
            a = a.reshape(1)
        m = np.isfinite(a)
        return a[m]

    def plot(self, persons):
        """
        Update plots with newest data from the persons.
        NOTE: 使用 setData 更新已存在的曲线，避免每帧 clear() 带来的卡顿。
        """
        if not persons:
            return

        person = persons[0]  # 当前 UI 仅展示第一个人，避免多人的反复重绘卡顿
        raw_plot, filtered_plot, spectrum_plot, bpm_plot, bp_plot = self.plots

        # ------- Signal -------
        raw = self._finite(getattr(person, 'corrected', None))
        if self._curves['raw'] is None:
            self._curves['raw'] = raw_plot.plot(raw)
        else:
            self._curves['raw'].setData(raw)

        # ------- Filtered -------
        flt = self._finite(getattr(person, 'filtered', None))
        if self._curves['filtered'] is None:
            self._curves['filtered'] = filtered_plot.plot(flt)
        else:
            self._curves['filtered'].setData(flt)

        # ------- Spectrum (x=freqs) -------
        spec = self._finite(getattr(person, 'spectrum', None))
        freqs = self._finite(getattr(person, 'freqs', None))
        # 对齐长度，防止越界
        n = min(len(spec), len(freqs))
        spec = spec[:n]
        freqs = freqs[:n]
        if self._curves['spectrum'] is None:
            self._curves['spectrum'] = spectrum_plot.plot(spec, x=freqs)
        else:
            # 某些 Plot 实现是 setData(y) / setData(x=x, y=y)
            try:
                self._curves['spectrum'].setData(freqs, spec)
            except TypeError:
                self._curves['spectrum'].setData(spec)

        # ------- BPM & Avg -------
        bpm = self._finite(getattr(person, 'bpm', None))
        if self._curves['bpm'] is None:
            self._curves['bpm'] = bpm_plot.plot(bpm)
        else:
            self._curves['bpm'].setData(bpm)

        av = self._finite(getattr(person, 'avBpm', None))
        if len(av):
            if self._curves['bpm_avg'] is None:
                # 原代码：bpm.plot(person.avBpm, pen=qt.Qt.red)
                self._curves['bpm_avg'] = bpm_plot.plot(av, pen=qt.Qt.red)
            else:
                try:
                    self._curves['bpm_avg'].setData(av)
                except Exception:
                    # 某些后端需要重建
                    self._curves['bpm_avg'] = bpm_plot.plot(av, pen=qt.Qt.red)

        # ------- Blood Pressure -------
        bp = self._finite(getattr(person, 'blood_pressure', None))
        if self._curves['bp'] is None:
            self._curves['bp'] = bp_plot.plot(bp)
        else:
            self._curves['bp'].setData(bp)
