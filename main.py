from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

class AbsensiRow(BoxLayout):
    def __init__(self, hari, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 95
        self.spacing = 6
        self.padding = [5, 2, 5, 2]

        # Label Hari (Font Besar 34)
        self.add_widget(Label(
            text=hari, 
            size_hint_x=0.15, 
            bold=True,
            font_size=34
        ))

        # 6 Kolom Input (3x In & Out) - Font Besar 34, Lebar proporsional
        self.inputs = []
        for i in range(6):
            ti = TextInput(
                text='', 
                multiline=False, 
                halign='center', 
                size_hint_x=0.115, 
                hint_text="--:--",
                font_size=34,
                padding_y=[(95 - 34) / 2 - 4, 0]
            )
            ti.bind(text=self.on_input_changed)
            ti.bind(focus=self.format_time_input)
            self.inputs.append(ti)
            self.add_widget(ti)

        # Label Total Jam (Font Besar 34)
        self.lbl_total = Label(
            text='', 
            bold=True, 
            font_size=34,
            size_hint_x=0.17,
            color=(0.3, 1.0, 0.4, 1)
        )
        self.add_widget(self.lbl_total)

        # Label Sisa Jam (Font Besar 34)
        self.lbl_sisa = Label(
            text='', 
            bold=True, 
            font_size=34,
            size_hint_x=0.17,
            color=(1.0, 0.4, 0.4, 1)
        )
        self.add_widget(self.lbl_sisa)

    def on_input_changed(self, *args):
        self.hitung_total()
        self.app_instance.hitung_keseluruhan()

    def format_time_input(self, instance, value):
        if not value:
            text = instance.text.strip()
            if text and text not in ["00:00", "0:00", "--:--"]:
                menit = self.parse_jam_ke_menit(text)
                if menit is not None:
                    h = menit // 60
                    m = menit % 60
                    instance.text = f"{h:02d}:{m:02d}"

    def hitung_total(self):
        vals = []
        has_input = False
        for ti in self.inputs:
            val = ti.text.strip()
            if val and val not in ["00:00", "0:00", "--:--"]:
                has_input = True
                vals.append(self.parse_jam_ke_menit(val))
            else:
                vals.append(None)

        total_menit = 0
        valid_minutes = [m for m in vals if m is not None]

        for i in range(0, len(valid_minutes) - 1, 2):
            menit_masuk = valid_minutes[i]
            menit_keluar = valid_minutes[i+1]
            
            if menit_keluar >= menit_masuk:
                total_menit += (menit_keluar - menit_masuk)

        if not has_input or len(valid_minutes) < 2:
            self.lbl_total.text = ""
            self.lbl_sisa.text = ""
            return 0

        jam = total_menit // 60
        menit = total_menit % 60
        self.lbl_total.text = f"{jam:02d}:{menit:02d}"

        target_menit = 9 * 60
        selisih_menit = total_menit - target_menit
        
        if selisih_menit >= 0:
            self.lbl_sisa.text = f"+{selisih_menit} m"
            self.lbl_sisa.color = (0.3, 1.0, 0.4, 1)
        else:
            self.lbl_sisa.text = f"{selisih_menit} m"
            self.lbl_sisa.color = (1.0, 0.4, 0.4, 1)

        return total_menit

    def parse_jam_ke_menit(self, teks_jam):
        if not teks_jam:
            return None
        teks_jam = teks_jam.strip()
        if not teks_jam or teks_jam in ["00:00", "0:00", "--:--"]:
            return None
        
        if ':' in teks_jam or '.' in teks_jam:
            teks_jam = teks_jam.replace('.', ':')
            parts = teks_jam.split(':')
            if len(parts) == 2:
                try:
                    h = int(parts[0])
                    m = int(parts[1])
                    if 0 <= h < 24 and 0 <= m < 60:
                        return h * 60 + m
                except ValueError:
                    return None
        else:
            if teks_jam.isdigit():
                val_len = len(teks_jam)
                if val_len == 4:
                    h = int(teks_jam[:2])
                    m = int(teks_jam[2:])
                elif val_len == 3:
                    h = int(teks_jam[0])
                    m = int(teks_jam[1:])
                elif val_len == 1 or val_len == 2:
                    h = int(teks_jam)
                    m = 0
                else:
                    return None
                
                if 0 <= h < 24 and 0 <= m < 60:
                    return h * 60 + m
        return None


class AbsensiApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Judul Aplikasi Diperbarui menjadi "ABSENSI" dengan ukuran font besar
        root.add_widget(Label(
            text='ABSENSI', 
            size_hint_y=None, 
            height=55, 
            font_size=40, 
            bold=True
        ))

        # Header Tabel (Font Besar 34)
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=6, padding=[5, 0, 5, 0])
        header.add_widget(Label(text='Hari', size_hint_x=0.15, bold=True, font_size=34))
        headers_jam = ['In 1', 'Out 1', 'In 2', 'Out 2', 'In 3', 'Out 3']
        for h in headers_jam:
            header.add_widget(Label(text=h, size_hint_x=0.115, bold=True, font_size=34))
        header.add_widget(Label(text='Total', size_hint_x=0.17, bold=True, font_size=34))
        header.add_widget(Label(text='Sisa', size_hint_x=0.17, bold=True, font_size=34))
        root.add_widget(header)

        # ScrollView untuk 5 baris hari (Senin - Jumat)
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=6, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        daftar_hari = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']
        self.rows_data = []

        for hari in daftar_hari:
            row = AbsensiRow(hari, self)
            grid.add_widget(row)
            self.rows_data.append(row)

        scroll.add_widget(grid)
        root.add_widget(scroll)

        # Baris Grand Total di bagian bawah (Font Besar 34)
        summary_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=55, spacing=6, padding=[5, 0, 5, 0])
        summary_layout.add_widget(Label(text='GRAND TOTAL', size_hint_x=0.15, bold=True, font_size=24, color=(1, 0.9, 0.2, 1)))
        
        # Spacer kosong sejajar 6 kolom input
        for _ in range(6):
            summary_layout.add_widget(Label(text='', size_hint_x=0.115))

        # Total Jam Keseluruhan (Font Besar 34)
        self.lbl_grand_total = Label(text='', bold=True, font_size=34, size_hint_x=0.17, color=(0.3, 1.0, 0.4, 1))
        summary_layout.add_widget(self.lbl_grand_total)

        # Total Sisa Keseluruhan (Font Besar 34)
        self.lbl_grand_sisa = Label(text='', bold=True, font_size=34, size_hint_x=0.17, color=(1.0, 0.4, 0.4, 1))
        summary_layout.add_widget(self.lbl_grand_sisa)
        
        root.add_widget(summary_layout)

        # Tombol Hitung Ulang
        btn_hitung = Button(
            text='Hitung Ulang Semua', 
            size_hint_y=None, 
            height=60,
            bold=True,
            font_size=26
        )
        btn_hitung.bind(on_press=self.on_hitung_semua)
        root.add_widget(btn_hitung)

        # Hitung awal saat aplikasi dibuka
        self.hitung_keseluruhan()

        return root

    def hitung_keseluruhan(self):
        total_menit_semua = 0
        total_target_menit = 0
        ada_aktivitas = False

        for row in self.rows_data:
            vals = []
            has_input = False
            for ti in row.inputs:
                val = ti.text.strip()
                if val and val not in ["00:00", "0:00", "--:--"]:
                    has_input = True
                    vals.append(row.parse_jam_ke_menit(val))
                else:
                    vals.append(None)
            
            valid_minutes = [m for m in vals if m is not None]
            if has_input and len(valid_minutes) >= 2:
                ada_aktivitas = True
                total_target_menit += 9 * 60  # Target 9 jam untuk hari yang terisi

            for i in range(0, len(valid_minutes) - 1, 2):
                m_in = valid_minutes[i]
                m_out = valid_minutes[i+1]
                if m_out >= m_in:
                    total_menit_semua += (m_out - m_in)

        if not ada_aktivitas and total_menit_semua == 0:
            self.lbl_grand_total.text = ""
            self.lbl_grand_sisa.text = ""
        else:
            g_jam = total_menit_semua // 60
            g_menit = total_menit_semua % 60
            self.lbl_grand_total.text = f"{g_jam:02d}:{g_menit:02d}"

            selisih_grand = total_menit_semua - total_target_menit
            if selisih_grand >= 0:
                self.lbl_grand_sisa.text = f"+{selisih_grand} m"
                self.lbl_grand_sisa.color = (0.3, 1.0, 0.4, 1)
            else:
                self.lbl_grand_sisa.text = f"{selisih_grand} m"
                self.lbl_grand_sisa.color = (1.0, 0.4, 0.4, 1)

    def on_hitung_semua(self, instance):
        for row in self.rows_data:
            row.hitung_total()
        self.hitung_keseluruhan()


if __name__ == '__main__':
    AbsensiApp().run()
